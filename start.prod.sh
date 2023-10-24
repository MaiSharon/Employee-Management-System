#!/bin/bash
set -e

# 編譯 Django 消息
echo "Compiling Django messages..."
django-admin compilemessages

# 嘗試連接到數據庫
echo "Attempting to connect to the database..."
until echo "from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW DATABASES'); print('db_mai' in [row[0] for row in cursor.fetchall()])" | python manage.py shell | grep "True"; do
    echo "Waiting for the database 'db_mai' to start"
    sleep 5
done
echo "Successfully connected to the database 'db_mai'"

# 執行數據庫遷移
echo "Running database migrations..."
python manage.py migrate

# 使用 Daphne 運行 Django 應用
echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8000 prj_dept.asgi:application
