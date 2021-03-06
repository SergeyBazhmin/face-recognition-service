from flask import jsonify, request
from background.celery_app import celery_pool, run_worker
import server
from server import app
from flask_jwt_extended import jwt_required
from functools import wraps
from common import settings
from server.websocket import socket_io
from common.constants import SERVER_SLEEP
from server.enumerates import Errors
import uuid
import json
import time


def maybe_jwt(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return jwt_required(func)(*args, **kwargs) if settings.server_settings.use_jwt else func(*args, **kwargs)

    return wrapper


@app.route('/ping', methods=['GET'], endpoint='f1')
def ping():
    return jsonify({'message': 'pong'})


@app.route('/workers/<worker_id>', methods=['DELETE'], endpoint='f4')
@maybe_jwt
def delete_worker(worker_id):
    celery_pool.control.revoke(worker_id, terminate=True)
    return jsonify({'id': worker_id})


@app.route('/workers/create', methods=['POST'], endpoint='f5')
@maybe_jwt
def post():
    new_worker_id = str(uuid.uuid4())
    run_worker.apply_async(task_id=new_worker_id)
    return jsonify({'id': new_worker_id})


@app.route('/image/recognize', methods=['POST'], endpoint='f6')
@maybe_jwt
def recognize():
    data = request.get_json()
    if data is None:
        return jsonify({'message': Errors.JSON_MISSING.value}), 400

    photo_base64 = data['photo']
    identifier = str(uuid.uuid4())
    response = {}

    server.redis_connection.rpush('recognition', json.dumps({'id': identifier, 'photo': photo_base64}))
    while True:
        recognition = server.redis_connection.get(identifier)
        if recognition is not None:
            recognition = json.loads(recognition.decode('utf-8'))
            if settings.server_settings.debug_recognition:
                socket_io.emit('recognition', {
                    'photo': photo_base64,
                    'person': recognition['person'],
                    'distance': recognition['distance']
                }, namespace='/debug')
            response['person'] = recognition['person']
            server.redis_connection.delete(identifier)
            break

        time.sleep(SERVER_SLEEP)

    return jsonify(response)


@app.route('/image/store', methods=['POST'], endpoint='f7')
@maybe_jwt
def store():
    data = request.get_json()
    if data is None:
        return jsonify({'message': Errors.JSON_MISSING.value}), 400

    photo_base64 = data['photo']
    person_id = data['person_id']
    server.redis_connection.rpush('storage',
                                  json.dumps({'photo': photo_base64, 'person_id': person_id}))
    return jsonify({'message': 'ok'})


