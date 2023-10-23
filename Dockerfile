# 使用輕量級的 Python 鏡像
FROM python:3.9-alpine

# 設置工作目錄
WORKDIR /data/prj_dept

# 設置環境變量，ARG只在建構過程中使用
ARG DJANGO_SETTINGS_MODULE=default_value

# 複製 requirements.txt 並安裝必要的包和庫，然後清理
COPY requirements.txt ./
RUN apk update && \
    apk add --no-cache gcc musl-dev libffi-dev mariadb-connector-c-dev gettext && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
#    pip install uwsgi && \
    apk del gcc musl-dev libffi-dev && \
    rm -rf /var/cache/apk/* && \
    ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo 'Asia/Taipei' >/etc/timezone

# 創建非root用戶和組
RUN addgroup -S daphne && adduser -S daphneuser -G daphne

COPY . .

# 保護敏感文件的暫時變量，ARG只在建構過程中使用
ARG SECRET_KEY=default_value
ARG ALLOWED_HOSTS=default_value
ARG MYSQL_NAME=default_value
ARG MYSQL_USER=default_value
ARG MYSQL_ROOT_PASSWORD=default_value
ARG MYSQL_PASSWORD=default_value
ARG MYSQL_HOST=default_value
ARG MYSQL_PORT=default_value
ARG REDIS_LOCATION=default_value
ARG CELERY_BROKER_URL=default_value
ARG CELERY_RESULT_BACKEND=default_value
ARG LINE_CHANNEL_ACCESS_TOKEN=default_value
ARG LINE_CHANNEL_SECRET=default_value

# 收集靜態文件
RUN python manage.py collectstatic --noinput

# 設置執行權限
RUN chmod +x /data/prj_dept/start.prod.sh

# 暴露端口
EXPOSE 8000

# 使用非root用戶運行容器
USER daphneuser
