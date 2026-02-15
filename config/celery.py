import os
from celery import Celery
from datetime import timedelta

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'config.settings'
)

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.broker_url = 'amqp://localhost'   # اگر Docker نداری
app.conf.result_backend = 'rpc://'
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'pickle'
app.conf.accept_content = ['json', 'pickle']
app.conf.result_expires = timedelta(days=1)
app.conf.worker_prefetch_multiplier = 4
