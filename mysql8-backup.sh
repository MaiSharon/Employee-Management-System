#!/bin/bash

# 加載.env文件
source .env.prod

# 定義其他變數
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_FILE="backup_$TIMESTAMP.sql"

# 執行備份
docker exec -T $CONTAINER_NAME /usr/bin/mysqldump -u $MYSQL_USER --password=$MYSQL_PASSWORD $MYSQL_NAME > $BACKUP_FILE

# 上傳到S3
aws s3 cp $BACKUP_FILE s3://$S3_BUCKET/$BACKUP_FILE

# 刪除本地備份
rm -f $BACKUP_FILE
