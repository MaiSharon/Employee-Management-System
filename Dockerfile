FROM python:3.9-alpine
WORKDIR /data/prj_dept
ENV server_params=
COPY requirements.txt ./

# 創建非root用戶和組
RUN addgroup -S uwsgi && adduser -S uwsgiuser -G uwsgi


# 安裝必要的包和庫，然後清理
RUN apk update && \
    apk add --no-cache gcc musl-dev libffi-dev mariadb-connector-c-dev gettext && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install uwsgi && \
    apk del gcc musl-dev libffi-dev && \
    rm -rf /var/cache/apk/* && \
    ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo 'Asia/Taipei' >/etc/timezone

# 將當前目錄（即 Dockerfile 所在的目錄）下的所有文件和子目錄複製到 WORKDIR 路徑中
COPY . .
# 設定日誌文件和靜態文件的權限
RUN touch /data/prj_dept/dept_app.performance.log && \
    touch /data/prj_dept/dept_app.task.log && \
    touch /data/prj_dept/dept_app.log && \
    chown uwsgiuser:uwsgi /data/prj_dept/dept_app.performance.log && \
    chown uwsgiuser:uwsgi /data/prj_dept/dept_app.task.log && \
    chown uwsgiuser:uwsgi /data/prj_dept/dept_app.log

# Change ownership of the entire project directory
# RUN chown -R uwsgiuser:uwsgi /data/prj_dept/
# RUN rm -rf /data/prj_dept/staticfiles/*

RUN chmod +x ./start.prod.sh
EXPOSE 8000

# 使用非root用戶運行容器
USER uwsgiuser
