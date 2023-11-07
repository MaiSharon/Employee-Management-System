import logging
import re

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django import forms
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_http_methods, require_POST


from dept_app import models
from dept_app.utils import email_utils
from dept_app.utils.bootstrap import BootStrapModelForm, BootStrapForm


logger = logging.getLogger(__name__)

class AdminModelForm(BootStrapModelForm):
    """
    表單用於管理員註冊: 用戶名、密碼和信箱的自定義驗證。
    """
    confirm_password = forms.CharField(
        label='確認密碼',
        widget=forms.PasswordInput(render_value=True),  # 當密碼不一致不清空，預設會自動清空# *****
    )

    class Meta:
        model = models.Admin
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),  # 當密碼不一致不清空，預設會自動清空# *****
        }

    def clean_username(self):
        """檢查用戶名是否只包含英文字母、數字、下劃線和點，並且用戶名不可重複"""
        username = self.cleaned_data.get('username')

        # 檢查用戶名是否只包含英文字母、數字、下劃線和點
        if not re.match(r'^[a-zA-Z0-9_.]+$', username):
            raise ValidationError('用戶名只能包含英文字母、數字、下劃線和點')

        # 檢查用戶名必須包含至少一個字母和一個數字
        if not (re.search(r'\d', username) and re.search(r'[a-zA-Z]', username)):
            raise ValidationError('用戶名必須包含至少一個字母和一個數字')

        # 檢查用戶名長度
        if len(username) < 8 or len(username) > 16:
            raise ValidationError('用戶名必須在8到16個字符之間')

        # 檢查用戶名是否已存在
        exists = models.Admin.objects.filter(username=username, is_verified=True).exists()
        if exists:
            raise ValidationError(f'{username} 此用戶名已經存在')
        print(username)
        return username


    def clean_password(self):
        """檢查密碼是否符合長度8~64、不含空格、含至少1個特殊字符"""
        password = self.cleaned_data.get('password')

        # 最小長度檢查
        if len(password) < 8:
            raise ValidationError('密碼長度必須至少為8個字符')

        if len(password) >= 65:
            raise ValidationError('密碼長度不可超過64個字符')

        if ' ' in password:
            raise ValidationError('密碼不能包含空格')

        if not any(char in '!@#$%^&*()-+_=<>?/[]' for char in password):
            raise ValidationError('密碼必須包含至少一個特殊字符')

        # Django內建的密碼強度檢查，已含最小長度檢查不可<8
        validate_password(password, self.instance)
        return password

    def clean_confirm_password(self):
        """檢查密碼確認是否一致、不可為空"""
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password is None:
            return confirm_password

        if password != confirm_password:
            raise ValidationError('密碼不一致')
        return confirm_password

    def clean_email(self):
        """檢查信箱驗證狀態"""
        email = self.cleaned_data.get('email')

        # 如果已有信箱但尚未通過驗證
        if models.Admin.objects.filter(email=email, is_verified=False).exists():
            raise ValidationError('此信箱尚未通過驗證，請點擊下方重發驗證信。')
        # 如果已有信箱和驗證
        elif models.Admin.objects.filter(email=email, is_verified=True).exists():
            raise ValidationError('此信箱已經註冊')
        else:
            return email


@require_http_methods(['GET', 'POST'])
def register(request):
    """
    處理用戶的創建。
    - GET請求：顯示空的註冊表單。
    - POST請求：驗證表單數據，創建新的用戶。
    """
    if request.method == 'GET':
        form = AdminModelForm()
        return render(request, 'register.html', {'form': form})

    form = AdminModelForm(data=request.POST)
    logger.info('Received GET request for admin registration.')
    if form.is_valid():
        admin = form.save(commit=False)
        admin.password = make_password(form.cleaned_data['password'])
        admin.save()
        # 發送驗證郵件
        email_utils.send_email_token(request, admin)
        messages.success(request, '驗證郵件已發送，請檢查您的信箱。')

        # Prepare the user data to send
        user_data = {
            'type': 'new_admin',
            'user': {
                'id': admin.id,
                'username': admin.username,
            },
        }

        # Send message to the WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('chat_general', user_data)

        # 記錄創建的用戶
        logger.info(f'Admin account created: {admin.username}, Email: [REDACTED]')
        return redirect('register')

    # 記錄失敗的註冊嘗試（敏感信息已脫敏）
    sanitized_errors = {k: '[REDACTED]' if k in ['password', 'email'] else v for k, v in form.errors.items()}
    logger.warning(f'Failed admin account creation attempt: {sanitized_errors}')
    # 表單驗證失敗，顯提示信息
    return render(request, 'register.html', {'form': form})

@require_GET
def verify_email(request, token):
    """
    驗證用戶的電子郵件。
    這個函數會解碼 URL 中的驗證碼，並查找對應的 Admin 對象。
    如果驗證成功，將會更新 Admin 對象的狀態。
    """
    try:
        # 解碼從URL中獲取的驗證碼
        email_token = force_str(urlsafe_base64_decode(token))
        if None != email_token:
            logger.info(f'Attempting to decode email token: {token[:5]}')
        # 查找對應的Admin對象
        admin = models.Admin.objects.get(email_token=email_token)

    except models.Admin.DoesNotExist:
        # 若無對應的Admin對象，可能是已驗證或無效驗證碼都到重新驗證頁面
        messages.success(request, '無效驗證碼或已驗證成功，請重發認證信或登入。')
        logger.warning(f'not Admin: is None')
        return redirect('re_verify')
    current_time = timezone.now()
    if current_time > admin.token_expiration:
        # 若驗證碼過期，到重新驗證輸入信箱頁面
        messages.success(request, '驗證碼已過期，請重新發送認證信。')
        logger.warning(f'Token for Admin object with email_token: {email_token[:5]} has expired.')
        return redirect('re_verify')

    # 若驗證成功，更新Admin對象的狀態並保存
    admin.is_verified = True
    admin.email_token = None
    admin.save()
    logger.info(f'Admin object with Username: {admin.username} is verified.')

    # 直接登入，進入管理員列表頁面
    request.session['info'] = {'id': admin.id, 'name': admin.username}
    # 設定session到期時間為24小時
    request.session.set_expiry(60 * 60 * 24)
    return redirect('admin_list')


class ReVerifyForm(BootStrapForm):
    """
    表單用於電子信箱的重發驗證信。
    信箱的自定義驗證。
    """
    email = forms.EmailField(label='請輸入您的信箱')

    def clean_email(self):
        """檢查信箱是否已註冊或是否未驗證"""
        email = self.cleaned_data.get("email")

        # 如果已有信箱但尚未通過驗證
        if models.Admin.objects.filter(email=email, is_verified=False).exists():
            admin_object = models.Admin.objects.get(email=email)
            current_time = timezone.now()
            if current_time > admin_object.email_send_time:
                return email
            else:
                raise ValidationError('請一分鐘後再嘗試註冊。')
        elif models.Admin.objects.filter(email=email, is_verified=True).exists():
            raise ValidationError("您已驗證成功，請直接登入。")
        else:
            raise ValidationError("此信箱未註冊，請重新輸入。")
        return email

@require_http_methods(['GET', 'POST'])
def re_verify(request):
    """
    驗證信件過期，重發驗證信。
    - GET請求：顯示空的信箱表單。
    - POST請求：驗證信箱表單數據，更新驗證碼有效期，發送驗證信。
    """
    if request.method == "GET":
        form = ReVerifyForm
        return render(request, 're-verify.html', {'form': form})

    form = ReVerifyForm(data=request.POST)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        # 獲取未通過驗證的信箱
        admin = models.Admin.objects.get(email=email, is_verified=False)
        # 更新驗證碼有效期
        admin.update_token_expiration()
        # 更新寄信紀錄時間
        admin.update_send_time()
        admin.save()

        # 發送驗證信
        email_utils.send_email_token(request, admin)
        messages.success(request, '驗證郵件已重新發送，請檢查您的信箱。')
        logger.info(f're-verify email send agine, email:{email[3:]}')
        return redirect('re_verify')
    # 表單驗證失敗，顯示提示訊息
    return render(request, 're-verify.html', {'form': form})

