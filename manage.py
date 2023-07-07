#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv


def load_env_file():
    """Get now .env file"""
    if os.getenv("DOCKER_ENV"):
        dotenv_path = '.env.docker'
    else:
        dotenv_path = '.env.local'

    load_dotenv(dotenv_path)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_dept.settings')
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.base')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    load_env_file()

    main()
