FROM python:3.9-alpine
WORKDIR /data/prj_dept
ENV server_params=
COPY requirements.txt ./
RUN apk update && \
    apk add --no-cache gcc musl-dev libffi-dev mariadb-connector-c-dev gettext && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apk del gcc musl-dev libffi-dev && \
    rm -rf /var/cache/apk/*

RUN ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo 'Asia/Taipei' >/etc/timezone

# install uWSGI
RUN pip install uwsgi

# 將當前目錄（即 Dockerfile 所在的目錄）下的所有文件和子目錄複製到 WORKDIR 路徑中
COPY . .

RUN chmod +x ./start.local.sh
EXPOSE 8000
# CMD ["/bin/sh", "/data/prj_dept/start.local.sh"]
