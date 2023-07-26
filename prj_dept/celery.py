import os
from celery import Celery
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_dept.settings')

app = Celery('prj_dept')

app.config_from_object('settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
