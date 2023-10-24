from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import logging

logger = logging.getLogger(__name__)

def send_email_token(request, admin):
    """
    發送帶有驗證連結的電子郵件。

    參數:
    - request: HttpRequest 對象，通常在視圖中傳遞。
    - admin: 模型實例，需要包含email和email_token字段。

    返回:
    - 無。這個函數會觸發一封電子郵件。
    """
    try:
        # 獲取當前網站的域名
        current_site = get_current_site(request).domain


        from django.conf import settings

        protocol = 'https' if settings.USE_HTTPS else 'http'

        # 生成有加密的驗證連結
        verification_link = f'{protocol}://{current_site}/verify/{urlsafe_base64_encode(force_bytes(admin.email_token))}'
        logo_link = f'{protocol}://{current_site}/static//logo-64.png'
        content = {
            'verification_link': verification_link,
            'logo_link': logo_link
        }

        # 使用HTML模板生成郵件內容
        html_message = render_to_string('email.html', content)


        # 郵件主題和純文本內容
        mail_subject = 'Quacqkersort.be - Email Verification'
        message = f'Please click on the link to confirm your email:\n{verification_link}'

        # 發送郵件
        send_mail(
            mail_subject,  # 主題
            message,  # 內容
            'ppp300a@gmail.com',  # 發件人
            [admin.email],  # 收件人列表
            html_message=html_message
        )
        logger.info('OK sent verify email to:[REDACTED]')
    except Exception as e:
        logger.error(f'Failed to send verify email: {str(e)}')