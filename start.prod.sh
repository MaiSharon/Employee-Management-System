#!/bin/bash
set -e

# django-admin compilemessages
django-admin compilemessages

# if local config file does not exist, clone one:
if [ ! -f "settings/local.py" ]; then
    echo "=== warning: local.py does not exist, will initialize the file, please update the configs ==="
    cp settings/production.py settings/local.py
    sed -i 's/DEBUG = False/DEBUG = False/g' settings/local.py
fi

# Try to connect to database using Django's manage.py shell
echo "=== Attempting to connect to the database ==="
until echo "from dept_app.models import Admin; print(Admin.objects.count())" | python manage.py shell $server_params ; do
    echo "Waiting for the database to start"
    sleep 2
done
echo "Database connection successful"


#RUN rm -rf /data/prj_dept/staticfiles/*

# Collect static files (--noinput ->It's say yes)
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput $server_params


# 使用 uWSGI 運行 Django 應用
exec uwsgi --ini /data/prj_dept/uwsgi.ini