# nexara_platform/celery.py

import os
from celery import Celery
from django.conf import settings

# Tell Celery which Django settings to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexara_platform.settings')

app = Celery('nexara')

# Pull Celery config from Django settings (all keys prefixed with CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in every installed app
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')