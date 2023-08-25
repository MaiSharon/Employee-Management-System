#!/bin/bash
set -e

# 翻譯文件
#django-admin compilemessages

# if local config file does not exist, clone one:
#if [ ! -f "settings/dev.py" ]; then
#    echo "=== warning: dev.py does not exist, will initialize the file, please update the configs ==="
#    cp settings/prod.py settings/dev.py
#    sed -i 's/DEBUG = False/DEBUG = False/g' settings/dev.py
#fi

# 嘗試使用 Django 的 manage.py shell 連接到數據庫並檢查 db_mai 數據庫
echo "=== Attempting to connect to the database ==="
until echo "from django.db import connection; cursor = connection.cursor(); cursor.execute('SHOW DATABASES'); print('db_mai' in [row[0] for row in cursor.fetchall()])" | python manage.py shell | grep "True"; do
    echo "Waiting for the database 'db_mai' to start"
    sleep 5
done
echo "Database 'db_mai' connection successful"


# synchronous web server for development:
python manage.py runserver 0.0.0.0:8000

