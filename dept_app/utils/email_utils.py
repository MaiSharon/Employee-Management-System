from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_email_token(request, admin):
    """
    發送帶有驗證連結的電子郵件。

    參數:
    - request: HttpRequest 對象，通常在視圖中傳遞。
    - instance: 模型實例，需要包含email和email_token字段。

    返回:
    - 無。這個函數會觸發一封電子郵件。
    """
    # 獲取當前網站的域名
    current_site = get_current_site(request).domain

    # 郵件主題
    mail_subject = 'Activate your account.'

    # 生成有加密的驗證連結
    verification_link = f'http://{current_site}/verify/{urlsafe_base64_encode(force_bytes(admin.email_token))}'

    # 郵件內容
    message = f'Please click on the link to confirm your email:\n{verification_link}'

    # 發送郵件
    send_mail(
        mail_subject,  # 主題
        message,  # 內容
        'ppp300a@gmail.com',  # 發件人
        [admin.email],  # 收件人列表
    )