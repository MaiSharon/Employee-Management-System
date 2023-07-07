#!/bin/bash
set -e

# django-admin compilemessages
django-admin compilemessages

# if local config file does not exist, clone one:
if [ ! -f "settings/local.py" ]; then
    echo "=== warning: local.py does not exist, will initialize the file, please update the configs ==="
    cp settings/production.py settings/local.py
    sed -i 's/DEBUG = False/DEBUG = True/g' settings/local.py
fi


# Try to connect to database using Django's manage.py check
echo "=== Attempting to connect to the database ==="
until python manage.py check $server_params; do
    echo "Waiting for the database to start"
    sleep 1
done
echo "Database connection successful"



# synchronous web server for development:
python manage.py runserver 0.0.0.0:8000 $server_params  #


# for async web server:
# export DJANGO_SETTINGS_MODULE=settings.local
# uvicorn prj_dept.asgi:application --workers 3
