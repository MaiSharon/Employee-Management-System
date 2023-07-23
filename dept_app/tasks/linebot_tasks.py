# Create your tasks here
from celery import shared_task
from dept_app.utils.util_linebot.linebot_client import send_greeting


@shared_task
def send_greeting_task(user_id, message):
    send_greeting(user_id, message)
