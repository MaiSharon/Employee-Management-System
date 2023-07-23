FROM python:3.9-alpine
WORKDIR /data/prj_dept
ENV server_params=
COPY dev_requirements.txt ./
RUN apk update && \
    apk add --no-cache gcc musl-dev libffi-dev mariadb-connector-c-dev gettext && \
    python3 -m pip install --upgrade pip && \
    pip install -r dev_requirements.txt && \
    apk del gcc musl-dev libffi-dev && \
    rm -rf /var/cache/apk/*

RUN ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo 'Asia/Taipei' >/etc/timezone

COPY . .
RUN chmod +x ./start.local.sh
EXPOSE 8000
# CMD ["/bin/sh", "/data/prj_dept/start.local.sh"]
