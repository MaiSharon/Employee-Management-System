# 使用 Python 3.9 的 Alpine 版本作為基本映像
FROM python:3.9-alpine

# 設置工作目錄
WORKDIR /data/prj_dept

# 設置環境變量
ENV server_params=

# 複製 requirements 文件
COPY requirements.txt ./

# 創建非 root 用戶和組
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

# 複製當前目錄的所有文件和子目錄到工作目錄
COPY . .

# 設定日誌文件和靜態文件的權限
RUN touch /data/prj_dept/dept_app.performance.log && \
    touch /data/prj_dept/dept_app.task.log && \
    touch /data/prj_dept/dept_app.log && \
    chown uwsgiuser:uwsgi /data/prj_dept/dept_app.*.log

# 設置執行權限
RUN chmod +x ./start.prod.sh

# 暴露端口
EXPOSE 8000

# 使用非 root 用戶運行容器
USER uwsgiuser

