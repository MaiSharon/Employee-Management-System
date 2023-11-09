#!/bin/bash

# 切換到腳本所在目錄
cd /home/ubuntu/projects/dept_manage/prj_dept/

# 加載.env文件
source .env.prod

# 定義其他變數
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_FILE="backup_$TIMESTAMP.sql"

# 執行備份
sudo docker compose -f docker-compose.prod.yml exec ${DOCKER_SERVICE_NAME} /usr/bin/mysqldump -uroot -p${MYSQL_ROOT_PASSWORD} ${MYSQL_NAME} > ${BACKUP_FILE}

# 上傳到S3
aws s3 cp $BACKUP_FILE s3://${S3_BUCKET}/${S3_BUCKET_FOLDER}/

# 刪除本地備份
rm -f $BACKUP_FILE
