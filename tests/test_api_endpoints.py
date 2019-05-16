import settings
import server
import redis
import pytest
from server.enumerates import Errors
from constants import ROOT_DIR
import json
import base64

static_folder = ROOT_DIR / 'tests' / 'static'
test_image = static_folder / '2_2.jpg'


@pytest.fixture(scope='module')
def client():
    '''Flask testing client'''
    server.app.testing = True
    server.redis_connection = redis.StrictRedis()
    test_client = server.app.test_client()

    return test_client


@pytest.mark.recognition
def test_recognition_request(client):
    settings.server_settings.use_jwt = False

    with open(test_image, "rb") as image_file:
        image_str = base64.b64encode(image_file.read()).decode('utf-8')

    response = client.post('/image/recognize', content_type='application/json', data=json.dumps({'photo': image_str}))
    assert response.status_code == 200

    json_data = json.loads(response.data)

    assert not json_data['denied']


@pytest.mark.recognition
def test_storage_request(client):
    settings.server_settings.use_jwt = False

    with open(test_image, "rb") as image_file:
        image_str = base64.b64encode(image_file.read()).decode('utf-8')

    response = client.post('/image/store', content_type='application/json', data=json.dumps({'photo': image_str}))
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert json_data['message'] == 'ok'


@pytest.mark.other
def test_json_missing(client):
    settings.server_settings.use_jwt = False
    response = client.post('/image/store')
    a = json.loads(response.data)
    assert a['message'] == Errors.JSON_MISSING.value


@pytest.mark.other
def test_jwt(client):
    settings.server_settings.use_jwt = True

    response = client.post('/image/store')
    data = json.loads(response.data)
    assert data['message'] == Errors.JWT_MISSING.value
    headers = {
        'Authorization': 'Bearer invalid-token'
    }
    response = client.post('/image/store', headers=headers)
    data = json.loads(response.data)
    assert data['message'] == Errors.JWT_INVALID.value


# @pytest.mark.celery
# def test_worker_creation(client):
#     utils.settings.server_settings.use_jwt = False


#
# @pytest.mark.celery
# def test_worker_creation(client):
#     settings.use_oauth = False
#
#     pool_inspect = celery_pool.control.inspect().active()
#     pool = list(pool_inspect)[0]
#     n_workers_before = len(list(map(lambda w: w['id'], pool_inspect[pool])))
#
#     response = client.get('/workers/create', content_type='application/json')
#     json_data = json.loads(response.data)
#     assert 'id'in json_data
#
#     worker_id = json_data['id']
#
#     pool_inspect = celery_pool.control.inspect().active()
#     pool = list(pool_inspect)[0]
#     n_workers_after = len(list(map(lambda w: w['id'], pool_inspect[pool])))
#
#     assert n_workers_after - n_workers_before == 1
#
#     p = Path("./static/image_1.jpg")
#     with open(p, "rb") as image_file:
#         image_str = base64.b64encode(image_file.read()).decode('utf-8')
#
#     response = client.post('/image/recognize', data=dict(photo=image_str))
#     json_data = json.loads(response.data)
#
#     assert 'denied' in json_data
#     assert not json_data['denied']
#
#     response = client.delete('/workers/{}'.format(worker_id))
#     json_data = json.loads(response.data)
#
#     assert 'id' in json_data
#     assert json_data['id'] == worker_id

#
# def test_ping(client):
#     response = client.get('/ping', content_type='application/json')
#     json_response = json.loads(response.data)
#     assert json_response['message'] == 'pong'





