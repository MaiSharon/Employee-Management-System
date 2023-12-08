from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_async_email(mail_subject, message, from_email, recipient_list, html_message):
    send_mail(
        mail_subject,
        message,
        from_email,
        recipient_list,
        html_message=html_message
    )