#!/bin/bash
set -e

# 編譯 Django 消息
django-admin compilemessages


# 嘗試使用 Django 的 manage.py shell 連接到數據庫並檢查 db_mai 數據庫
echo "=== Attempting to connect to the database ==="
until echo "from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW DATABASES'); print('db_mai' in [row[0] for row in cursor.fetchall()])" | python manage.py shell | grep "True"; do
    echo "Waiting for the database 'db_mai' to start"
    sleep 5
done
echo "Database 'db_mai' connection successful"

# 執行數據庫遷移
echo "=== Running database migrations ==="
#python manage.py makemigrations
python manage.py migrate

# 創建管理員用戶
echo "=== Creating admin user if not exists ==="
python create_admin.py

# 使用 uWSGI 運行 Django 應用
exec uwsgi --ini /data/prj_dept/uwsgi.ini
