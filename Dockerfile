FROM python:3.9
WORKDIR /data/prj_dept
ENV server_params=
COPY requirements.txt ./

# 創建非root用戶和組
RUN addgroup --system uwsgi && adduser --system --ingroup uwsgi uwsgiuser

# 安裝必要的包和庫，然後清理
RUN apt-get update && \
    apt-get install -y gcc libffi-dev libmariadbclient-dev gettext && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install uwsgi && \
    apt-get remove -y gcc libffi-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo 'Asia/Taipei' >/etc/timezone

# 將當前目錄（即 Dockerfile 所在的目錄）下的所有文件和子目錄複製到 WORKDIR 路徑中
COPY . .

RUN chmod +x ./start.prod.sh
EXPOSE 8000

# 使用非root用戶運行容器
USER uwsgiuser
