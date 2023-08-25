"""
Django settings for prj_dept project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os.path
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = Path.joinpath(BASE_DIR, 'templates')
LOG_DIR = "/data/logs/recruitment/"


ALLOWED_HOSTS = ["127.0.0.1"]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dept_app.apps.DeptAppConfig',
    'debug_toolbar',
    'rest_framework',
    'celery',
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # django debug toolbar
    'dept_app.performance.performance_logger_middleware',  # 性能紀錄要放在最上面，下面執行時才能抓到紀錄
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # "django.middleware.cache.UpdateCacheMiddleware",  # redis
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.cache.FetchFromCacheMiddleware",  # redis
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dept_app.middleware.auth.AuthMiddleware',
]
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]




ROOT_URLCONF = 'prj_dept.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'prj_dept.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        "OPTIONS": {
            "min_length": 8
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'

LANGUAGE_CODE = 'zh-hant'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Logging ，Django沿用了Python的dictConfig方式
LOGGING = {
    'version': 1,  # logging 設定格式版本，目前只有版本 1
    'disable_existing_loggers': False,  # 是否禁止所有已存在的 logger /Django有內痔的日誌，可設定為否

    'formatters': {  # 訊息輸出格式的定義
        'simple': {  # 一個名為 'simple' 的 formatter
            'format': '%(asctime)s -%(name)-12s %(lineno)d %(levelname)-8s %(message)s',  # 設定輸出的格式
        },
    },
    'handlers': {  # 處理器的定義，負責處理日誌訊息的輸出
        'console': {
            'class': 'logging.StreamHandler',  # 將日誌內容輸出到控制台中
            'formatter': 'simple',  # 這個處理器使用的 formatter
        },
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler',  # 負責日誌輸出到信件中
        # },
        'file': {
            # 'level': 'INFO',
            'class': 'logging.FileHandler',  # 使用的處理器類型
            'formatter': 'simple',  # 這個處理器使用的 formatter
            'filename': os.path.join(BASE_DIR, 'dept_app.log'),  # 日誌輸出到這個檔案
        },
        'task': {
            # 'level': 'INFO',
            'class': 'logging.FileHandler',  # 使用的處理器類型
            'formatter': 'simple',  # 這個處理器使用的 formatter
            'filename': os.path.join(BASE_DIR, 'dept_app.task.log'),  # 日誌輸出到這個檔案
        },
        'performance': {
            # 'level': 'INFO',
            'class': 'logging.FileHandler',  # 使用的處理器類型
            'formatter': 'simple',  # 這個處理器使用的 formatter
            'filename': os.path.join(BASE_DIR, 'dept_app.performance.log'),  # 日誌輸出到這個檔案
        },
    },

    'root': {  # 根 logger 的設定
        'handlers': ['console', 'file'],  # 會將日誌發送到這兩個處理器
        'level': 'INFO',  # 只有 "INFO"、"WARNING"、"ERROR" 和 "CRITICAL" 這四種級別的日誌會被記錄，而 "DEBUG" 級別的日誌會被忽略
    },

    'loggers': {  # 自定義 logger 的設定，可以指定只捕捉局部模塊發送的日誌
        "dept_app": {  # 自定義的日誌設定
            "handlers": ["console", "file"],  # 套用前面的處理器
            "level": "DEBUG",  # 這個 logger 的日誌級別，將會覆蓋root
        },

        "dept_app.task": {  # 只for views.task此模塊使用
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
