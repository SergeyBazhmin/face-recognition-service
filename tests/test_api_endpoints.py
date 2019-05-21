import pytest
import server
from server.enumerates import Errors
from common.constants import ROOT_DIR
import json
import redis
from common import settings
import base64

static_folder = ROOT_DIR / 'tests' / 'static'
test_image = static_folder / '2_2.jpg'


def is_redis_available():
    try:
        server.redis_connection.get('random_string')
    except (redis.exceptions.ConnectionError,
            redis.exceptions.BusyLoadingError):
        return False
    return True


@pytest.fixture(scope='module')
def client(request):
    '''Flask testing client'''
    server.app.testing = True
    server.app.config['JWT_SECRET_KEY'] = 'secret-key'
    test_client = server.app.test_client()
    if not is_redis_available():
        pytest.fail('redis server is not available, check your connection')

    response = test_client.post('/workers/create', content_type='application/json', data={})
    assert response.status_code == 200
    id = json.loads(response.data)['id']

    def finalizer():
        settings.server_settings.use_jwt = False
        response = test_client.delete(f'/workers/{id}')
        assert response.status_code == 200

    request.addfinalizer(finalizer)
    return test_client


@pytest.mark.recognition
def test_recognition_request(client):
    if not is_redis_available():
        pytest.fail('redis server is not available, check your connection')

    settings.server_settings.use_jwt = False

    with open(test_image, "rb") as image_file:
        image_str = base64.b64encode(image_file.read()).decode('utf-8')

    response = client.post('/image/recognize', content_type='application/json', data=json.dumps({'photo': image_str}))
    assert response.status_code == 200

    json_data = json.loads(response.data)

    assert json_data['person'] != -1


@pytest.mark.recognition
def test_storage_request(client):
    if not is_redis_available():
        pytest.fail('redis server is not available, check your connection')

    settings.server_settings.use_jwt = False

    with open(test_image, "rb") as image_file:
        image_str = base64.b64encode(image_file.read()).decode('utf-8')

    response = client.post('/image/store',
                           content_type='application/json',
                           data=json.dumps({'photo': image_str, 'person_id': 4}))
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
