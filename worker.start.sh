echo $DJANGO_SETTINGS_MODULE
DJANGO_SETTINGS_MODULE=settings.local celery -A prj_dept worker -l INFO -P solo

