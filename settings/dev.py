from dotenv import load_dotenv
from .base import *
import os

load_dotenv('./.env.dev')

# Unable HTTPS
USE_HTTPS = False

# Django settings
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

# 錯誤提示的語言
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ('zh-hant', _('Traditional Chinese')),
]
# 語言碼
LANGUAGE_CODE = 'zh-hant'
# 台北時區
TIME_ZONE = 'Asia/Taipei'

# **************************
# * Debug Toolbar Config *
# * Install apps *
# **************************
INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = ['127.0.0.1',]

# **************************
# * Database Config *
# * Use MySQL *
# **************************
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_NAME'),
        'USER': os.getenv('MYSQL_USER'),
        'PASSWORD': os.getenv('MYSQL_ROOT_PASSWORD'),
        'HOST': os.getenv('MYSQL_HOST'),
        'PORT': os.getenv('MYSQL_PORT'),
    }
}

# **************************
# * Cache Config *
# * Use Redis *
# **************************
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv('REDIS_LOCATION'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        }
    }
}

# **************************
# * Channels(websocket) Config *
# **************************
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# **************************
# * Celery Config *
# * For asynchronous task processing and scheduled tasks *
# **************************
CELERY_TIMEZONE = 'Asia/Taipei'
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# **************************
# * Log Config *
# **************************
LOGGING = {
    'version': 1,  # logging 設定格式版本，目前只有版本 1
    'disable_existing_loggers': False,  # 是否禁止所有已存在的 logger /Django有內建的日誌，可設定為否
    'formatters': {  # 訊息輸出格式的定義
        'standard': {
            'format': '[timestamp:%(asctime)s] [file_info:%(filename)s:%(lineno)d] [func_info:%(module)s:%(funcName)s] '
                      '[level:%(levelname)s]- message:%(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S+08:00'},

        'simple': {  # 簡單格式
            'format': '%(levelname)s %(message)s'
        },
    },

    'handlers': {  # 處理器，負責處理日誌訊息的輸出
        'console': {
            'class': 'logging.StreamHandler',  # 將日誌內容輸出到控制台中
            'formatter': 'standard',  # 這個處理器使用的 formatter
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',  # 使用的處理器類型
            'formatter': 'standard',  # 這個處理器使用的 formatter
            'filename': os.path.join(BASE_DIR, 'monitoring_PLG_configs', 'logs', 'dept_app.log'),  # 日誌輸出到這個檔案
        },
        'task': {   # 若有後台任務適合用（ Celery ）
            'level': 'INFO',
            'class': 'logging.FileHandler',  # 使用的處理器類型
            'formatter': 'standard',  # 這個處理器使用的 formatter
            'filename': os.path.join(BASE_DIR, 'monitoring_PLG_configs', 'logs', 'dept_app.task.log'),  # 日誌輸出到這個檔案
        },
        'performance': {  # 性能日誌
            'level': 'INFO',
            'class': 'logging.FileHandler',  # 使用的處理器類型
            'formatter': 'simple',  # 這個處理器使用的 formatter
            'filename': os.path.join(BASE_DIR, 'monitoring_PLG_configs', 'logs', 'dept_app.performance.log'),  # 日誌輸出到這個檔案
        },
        'views_task': {  # 特定模塊，任務功能日誌
            'level': 'INFO',
            'class': 'logging.FileHandler',  # 使用的處理器類型
            'formatter': 'standard',  # 這個處理器使用的 formatter
            'filename': os.path.join(BASE_DIR, 'monitoring_PLG_configs', 'logs', 'dept_app.views.task.log'),  # 日誌輸出到這個檔案
        },
    },

    'root': {  # 根 logger 的設定，補捉整個 Django 應用（包括所有模塊和 apps）
        'handlers': ['console', 'file'],  # 會將日誌發送到這兩個處理器
        'level': 'INFO',  # 只有 "INFO"、"WARNING"、"ERROR" 和 "CRITICAL" 這四種級別的日誌會被記錄，而 "DEBUG" 級別的日誌會被忽略
    },

    'loggers': {  # 自定義 logger 的設定，可以指定只捕捉局部模塊發送的日誌
        "dept_app": {  # 自定義的日誌設定
            "handlers": ["console", "file"],  # 套用前面的處理器
            "level": "DEBUG",  # 這個 logger 的日誌級別，將會覆蓋root
            "propagate": False,
        },

        "dept_app.task": {  # 若有後台任務（ Celery ）
            "handlers": ["console", "task"],
            "level": "INFO",
            "propagate": False,  # 是否將日誌訊息傳播到父 logger
        },
        "dept_app.performance": {  # 紀錄全局性能也就是請求與響應時間，並有安裝在Middleware上
            "handlers": ["console", "performance"],
            "level": "INFO",
            "propagate": False,  # 是否將日誌訊息傳播到父 logger
        },
    },
}

INSTALLED_APPS += [
    # ... other installed apps
    'drf_yasg',
]


# sentry setting
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
# sentry_sdk.init(
#     dsn="http://dbd1d4644ff4b5c9ec8c3d259c96ac8a@localhost:9000/2",
#     integrations=[DjangoIntegration()],
#     # 採樣率，1.0為100%，每一 url請求都記錄性能
#     traces_sample_rate=1.0,
#
#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     send_default_pii=True,
# )