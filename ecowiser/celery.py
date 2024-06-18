
# ecowiser/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecowiser.settings')
app = Celery('ecowiser')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.update(
    worker_concurrency=4,  # Adjust this number based on your server's capabilities
)
