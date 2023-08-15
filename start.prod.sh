#!/bin/bash
set -e

# 編譯 Django 消息
django-admin compilemessages

# 如果本地配置文件不存在，則複製一個
if [ ! -f "settings/local.py" ]; then
    echo "=== warning: local.py does not exist, will initialize the file, please update the configs ==="
    cp settings/production.py settings/local.py
    sed -i 's/DEBUG = False/DEBUG = False/g' settings/local.py
fi

# 嘗試使用 Django 的 manage.py shell 連接到數據庫
echo "=== Attempting to connect to the database ==="
until echo "from dept_app.models import Admin; print(Admin.objects.count())" | python manage.py shell; do
    echo "Waiting for the database to start"
    sleep 2
done
echo "Database connection successful"

# 收集靜態文件
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

# 更改靜態文件的所有權
echo "=== Changing ownership of static files ==="
chown -R www-data:www-data /data/prj_dept/staticfiles

# 使用 uWSGI 運行 Django 應用
exec uwsgi --ini /data/prj_dept/uwsgi.ini
