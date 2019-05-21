import psutil
from flask_socketio import SocketIO
from background.celery_app import celery_pool
from common import settings as s
from server import app


socket_io = SocketIO(app, async_mode='eventlet')
req_counter = 0
resp_counter = 0


@app.before_request
def request_counter():
    global req_counter
    req_counter += 1


@app.after_request
def response_counter(response):
    global resp_counter
    resp_counter += 1
    return response


@socket_io.on('debug', namespace='/debug')
def set_debug(debug):
    s.server_settings.debug_recognition = debug


@socket_io.on('poll_data')
def get_data():
    global req_counter, resp_counter
    vm = psutil.virtual_memory()
    pc_info = {
        'RAM': {
            'total': round(vm.total / 1024 / 1024, 2),
            'available': round(vm.available / 1024 / 1024, 2),
            'utilization (%)': vm.percent,
            'used': round(vm.used / 1024 / 1024, 2),
            'free': round(vm.free / 1024 / 1024, 2)
        },
        'CPU': {
            'cores': psutil.cpu_count(),
            'utilization (%)': psutil.cpu_percent()
        },
        'nrequests': req_counter,
        'nresponses': resp_counter,
    }
    socket_io.emit('data', pc_info)
    req_counter = 0
    resp_counter = 0


@socket_io.on('poll_workers')
def get_workers():
    i = celery_pool.control.inspect().active()
    pool = list(i)[0]
    workers = list(map(lambda w: w['id'], i[pool]))
    socket_io.emit('workers', workers)

