from settings import settings
from celery import Celery
from background.adapters import adapter_registry
from background.interfaces import Preprocessing
from importlib import import_module
from constants import WORKER_SLEEP
from background.adapters.db_enumerates import Database
from PIL import Image
import numpy as np
import time
from io import BytesIO
import base64
import redis
import json


celery_pool = Celery('tasks', broker='redis://{}:{}/{}'.format(
    settings.redis_configuration.host,
    settings.redis_configuration.port,
    settings.redis_configuration.db
))

priority_list = ['recognition', 'storage']


def run_celery():
    celery_pool.start(argv=['celery', 'worker', '-l', 'info'])


def base64_decode_image(img):
    img = Image.open(BytesIO(base64.b64decode(img)))
    return np.asarray(img)


def connect_to_databases():
    db_embeddings = adapter_registry[Database(settings.database_configuration.provider)](
        **settings.database_configuration.table_info
    )
    db_embeddings.connect(
        database=settings.database_configuration.database,
        user=settings.database_configuration.user,
        password=settings.database_configuration.password,
        host=settings.database_configuration.host,
        port=int(settings.database_configuration.port)
    )
    redis_connection = redis.StrictRedis(
        host=settings.redis_configuration.host,
        port=int(settings.redis_configuration.port),
        db=int(settings.redis_configuration.db)
    )
    return db_embeddings, redis_connection


def get_image_processing_instances():
    prep_cls = Preprocessing

    if settings.preprocessing_configuration is not None:
        prep_module = import_module(settings.preprocessing_configuration.module)
        prep_cls = getattr(prep_module, settings.preprocessing_configuration.class_name)

    model_module = import_module(settings.model_configuration.module)
    model_cls = getattr(model_module, settings.model_configuration.class_name)

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
                print(who)
                redis_connection.set(payload['id'], json.dumps({'person': who, 'distance': round(distance, 2)}))
            else:
                embedding = model_instance(np_img)
                db_connection.add_embedding(embedding, payload['id'])

        time.sleep(WORKER_SLEEP)
