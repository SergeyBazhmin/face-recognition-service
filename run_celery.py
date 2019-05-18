import os
from background.celery_app import run_celery

if __name__ == '__main__':
    os.environ['FORKED_BY_MULTIPROCESSING'] = '1'
    run_celery()
