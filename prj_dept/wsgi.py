"""
WSGI config for prj_dept project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import sys

from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application


def load_env_file():
    """Get now .env file need use docker compose"""
    if os.environ.get('DJANGO_ENV') == 'dev':
        dotenv_path = '.env.dev'
    elif 'runserver' in sys.argv:
        dotenv_path = '.env.dev'
    else:
        dotenv_path = '.env.test'
    load_dotenv(dotenv_path)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_dept.settings')

load_env_file()
application = get_wsgi_application()
