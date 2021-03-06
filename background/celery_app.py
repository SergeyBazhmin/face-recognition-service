from common.settings import celery_settings
from celery import Celery
from background.adapters import adapter_registry
from background.interfaces import Preprocessing
from importlib import import_module
from common.constants import WORKER_SLEEP
from background.adapters.db_enumerates import Database
from PIL import Image
import numpy as np
import time
from io import BytesIO
import base64
import redis
import json


celery_pool = Celery('tasks', broker='redis://{}:{}/{}'.format(
    celery_settings.redis_configuration.host,
    celery_settings.redis_configuration.port,
    celery_settings.redis_configuration.db
))

priority_list = ['recognition', 'storage']


def run_celery():
    celery_pool.start(argv=['celery', 'worker', '-l', 'info'])


def base64_decode_image(img):
    img = Image.open(BytesIO(base64.b64decode(img)))
    return np.asarray(img)


def connect_to_databases():
    db_embeddings = adapter_registry[Database(celery_settings.database_configuration.provider)](
        **celery_settings.database_configuration.table_info
    )
    db_embeddings.connect(
        database=celery_settings.database_configuration.database,
        user=celery_settings.database_configuration.user,
        password=celery_settings.database_configuration.password,
        host=celery_settings.database_configuration.host,
        port=int(celery_settings.database_configuration.port)
    )
    redis_connection = redis.StrictRedis(
        host=celery_settings.redis_configuration.host,
        port=int(celery_settings.redis_configuration.port),
        db=int(celery_settings.redis_configuration.db)
    )
    return db_embeddings, redis_connection


def get_image_processing_instances():
    prep_cls = Preprocessing

    if celery_settings.preprocessing_configuration is not None:
        prep_module = import_module(celery_settings.preprocessing_configuration.module)
        prep_cls = getattr(prep_module, celery_settings.preprocessing_configuration.class_name)

    model_module = import_module(celery_settings.model_configuration.module)
    model_cls = getattr(model_module, celery_settings.model_configuration.class_name)

    return prep_cls(), model_cls()


@celery_pool.task()
def run_worker():

    db_connection, redis_connection = connect_to_databases()

    preprocessing_instance, model_instance = get_image_processing_instances()

    print('model has been loaded')

    while True:
        task = None
        for q_task in priority_list:
            queue_size = redis_connection.llen(name=q_task)
            if queue_size:
                task = q_task
                break

        if task is not None:
            payload = json.loads(redis_connection.lpop(task).decode('utf-8'))
            np_img = base64_decode_image(payload['photo'])
            np_img = preprocessing_instance(np_img)

            if task == 'recognition':
                embedding = model_instance(np_img)
                who, distance = db_connection.select_similar(embedding)
                print(who, distance)
                redis_connection.set(payload['id'], json.dumps({'person': who, 'distance': distance}))
            else:
                embedding = model_instance(np_img)
                db_connection.add_embedding(embedding, payload['person_id'])

        time.sleep(WORKER_SLEEP)
