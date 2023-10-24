# prod.py
from dotenv import load_dotenv
from .base import *
import os

USE_HTTPS = True

load_dotenv('./.env.prod')
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

# 台北時區
TIME_ZONE = 'Asia/Taipei'


# 錯誤提示的語言
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ('zh-hant', _('Traditional Chinese')),
]
# 語言碼
LANGUAGE_CODE = 'zh-hant'


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


# 緩存
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


# Celery Configuration Options
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Taipei'


INSTALLED_APPS += [
    # your apps here
]

# for https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# websocket---------
# Channel layer settings for Websocket use
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.getenv('REDIS_LOCATION'))],
        },
    },
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[WEB_LOG] [timestamp:%(asctime)s] [file_info:%(filename)s:%(lineno)d] [func_info:%(module)s:%(funcName)s] '
                      '[level:%(levelname)s]- message:%(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S+08:00'},
        'simple': {
            'format': '[WEB_LOG] %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'error_console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
            'formatter': 'standard',
        },
        'performance_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'dept_app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'dept_app.errors': {
            'handlers': ['error_console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'dept_app.performance': {
            'handlers': ['performance_console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
