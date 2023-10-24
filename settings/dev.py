# dev.py
from dotenv import load_dotenv
from .base import *
import os

USE_HTTPS = False

load_dotenv('./.env.dev')

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(' ')

# 台北時區
TIME_ZONE = 'Asia/Taipei'

# 錯誤提示的語言
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ('zh-hant', _('Traditional Chinese')),
]
# 語言碼
LANGUAGE_CODE = 'zh-hant'


# Debug Toolbar settings
INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = [
    "127.0.0.1",
]


# MySQL setting
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


# 緩存使用 redis 當緩存
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


# Channel layer settings for Websocket use
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

INSTALLED_APPS += {
    # your apps here
}

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