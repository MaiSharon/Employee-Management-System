import logging
import re

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django import forms
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_http_methods

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from dept_app import models
from dept_app.utils import email_utils
from dept_app.utils.bootstrap import BootStrapModelForm, BootStrapForm

logger = logging.getLogger(__name__)

class AdminModelForm(BootStrapModelForm):
    """
    表單用於用戶註冊。負責處理自定義驗證用戶名、密碼和信箱。

    Attributes:
        confirm_password (CharField): 二次確認密碼輸入框

    Methods:
        clean_username: 確認用戶名的規範和唯一性
        clean_email: 確認信箱的唯一性和驗證狀態
        clean_password: 確認密碼的規範
        clean_confirm_password: 確認密碼確認字段與密碼字段匹配
    """
    confirm_password = forms.CharField(
        label='確認密碼',
        widget=forms.PasswordInput(render_value=True),  # 當密碼不一致不清空，預設會自動清空
    )

    class Meta:
        model = models.Admin
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),  # 當密碼不一致不清空，預設會自動清空# *****
        }

    def clean_username(self):
        """
        驗證用戶名符合規範。

        - 確認用戶名只包含英文字母、數字、下劃線和點。
        - 確認用戶名至少包含一個字母和一個數字。
        - 確認用戶名長度是否在 8 到 16 個字符之間。
        - 確認用戶名在系統中是唯一的。

        Returns:
            str: 驗證通過的用戶名。

        Raises:
            ValidationError: 用戶名不符合上述規範。
        """
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
        return username

    def clean_email(self):
        """
        驗證電子信箱的註冊和驗證狀態。

        - 確認電子信箱是否已註冊。
        - 確認電子信箱是否已通過驗證。

        Returns:
            str: 未註冊或已驗證的電子信箱。

        Raises:
            ValidationError: 電子信箱已註冊但未驗證，或已經註冊且已驗證。
        """
        email = self.cleaned_data.get('email')

        # 如果已有信箱但尚未通過驗證
        if models.Admin.objects.filter(email=email, is_verified=False).exists():
            raise ValidationError('此信箱尚未通過驗證，請點擊下方重發驗證信。')
        # 如果已有信箱和驗證
        elif models.Admin.objects.filter(email=email, is_verified=True).exists():
            raise ValidationError('此信箱已經註冊')
        else:
            return email

    def clean_password(self):
        """
        驗證密碼符合規範。

        - 確認密碼長度在 8 到 64 個字符之間。
        - 確認密碼是否含有至少一個特殊字符。
        - 確認密碼中不含有空格。

        Returns:
            str: 驗證通過的密碼。

        Raises:
            ValidationError: 密碼不符合上述規範。
        """
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
        """
        驗證確認密碼與原密碼一致。

        Returns:
            str: 驗證通過的確認密碼。

        Raises:
            ValidationError: 確認密碼與原密碼不一致。
        """
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password is None:
            return confirm_password

        if password != confirm_password:
            raise ValidationError('密碼不一致')
        return confirm_password

@require_http_methods(['GET', 'POST'])
def register(request):
    """
    處理用戶註冊請求。

    - GET: 返回空白註冊表單(AdminModelForm)。
    - POST: 處理提交的註冊數據以創建新用戶。

    Steps for GET: 創建並渲染空的 AdminModelForm。

    Steps for POST:
        1. 驗證註冊表單。
        2. 若驗證成功
            2.1. 創建並保存新的 Admin 對象。
            2.2. 發送驗證信給新用戶。
            2.3. 發送新用戶的數據到 WebSocket。
            2.4. 記錄創建操作，返回註冊頁面。
        3. 若驗證失敗
            3.1. 記錄操作，顯示錯誤信息並重渲染表單。

    Args:
        request (HttpRequest): 客戶端 HTTP 請求。

    Returns HttpResponse:
        - GET: 渲染過的註冊頁面，含空白 AdminModelForm。
        - POST:
            - 成功，重定向註冊頁面，含收信提示訊息。
            - 失敗，重渲染註冊頁面，含錯誤信息和空白 AdminModelForm。
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

        # 獲取當前域名
        current_site_domain = get_current_site(request).domain
        # 發送驗證信
        email_utils.send_async_email_token(admin, current_site_domain)
        messages.success(request, '驗證信已發送，請檢查您的信箱。')

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
    處理電子信箱的驗證請求。負責更新用戶(Admin 對象)的驗證狀態。

    - GET: 用 URL 中的驗證碼來查找對應的用戶(Admin 對象)並更新驗證狀態。

    Steps for GET:
    1. 從 URL 中解碼驗證碼。
    2. 使用解碼後的驗證碼查找對應的 Admin 對象。
    3. 若找不到對應的 Admin 對象，返回提示重發驗證信或登入。
    4. 若驗證碼已過期，重定向到重發驗證信頁面。
    5. 若驗證成功，更新 Admin 對象的驗證狀態並重定向到管理員列表頁面。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。
        token (str): URL 中的驗證碼。

    Returns HttpResponse:
        - GET: 重定向到管理員列表頁面或重發驗證信頁面。
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
        messages.success(request, '無效驗證碼，請嘗試重發認證信或登入。')
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

    # 驗證成功後直接登入，進入管理員列表頁面
    request.session['info'] = {'id': admin.id, 'name': admin.username}
    # 設定session到期時間為24小時
    request.session.set_expiry(60 * 60 * 24)
    return redirect('admin_list')

class ReVerifyForm(BootStrapForm):
    """
    表單用於重發驗證信。負責處理自定義驗證電子信箱。

    Attributes:
        email (EmailField): 電子信箱輸入框

    Methods:
        clean_email: 驗證電子信箱是否符合重發驗證信
    """
    email = forms.EmailField(label='請輸入您的信箱')

    def clean_email(self):
        """
        驗證電子信箱符合重發驗證信規範。

        steps:
        1. 驗證電子信箱是否已存在且未通過驗證。
            1.1. 若是則進行重發驗證信。
            1.1. 若用戶在一分鐘內頻繁輸入，提示用戶稍後嘗試。
        2. 若電子信箱已驗證，則提示用戶直接登入。
        3. 若電子信箱不存在，則提示用戶該信箱未註冊。

        Returns:
            str: 驗證通過的電子信箱。

        Raises:
            ValidationError: 電子信箱不符合上述規範。
        """
        email = self.cleaned_data.get('email')

        # 如果已有信箱但尚未通過驗證
        if models.Admin.objects.filter(email=email, is_verified=False).exists():
            admin_object = models.Admin.objects.get(email=email)
            current_time = timezone.now()
            if current_time > admin_object.email_send_time:
                return email
            else:
                raise ValidationError('請一分鐘後再嘗試註冊。')
        elif models.Admin.objects.filter(email=email, is_verified=True).exists():
            raise ValidationError('您已驗證成功，請直接登入。')
        else:
            raise ValidationError('此信箱未註冊，請重新輸入。')
        return email

@require_http_methods(['GET', 'POST'])
def re_verify(request):
    """
    處理重發電子信箱驗證信的請求。

    - GET: 返回空白重發驗證信表單( ReVerifyForm)。
    - POST: 處理提交的信箱數據並重發驗證信。

    Steps for GET: 創建並渲染空的 ReVerifyForm。

    Steps for POST:
    1. 驗證表單數據。
    2. 若驗證成功，更新對應用戶的驗證碼有效期和寄信紀錄時間。
        2.1. 發送驗證信至用戶信箱。
        2.2. 提示用戶收信並返回重發驗證信頁面，記錄發信操作。
    5. 若驗證失敗，顯示錯誤信息並重新渲染表單。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。

    Returns HttpResponse:
        - GET: 返回重發驗證信頁面，含空白 ReVerifyForm 表單。
        - POST:
            - 信箱有效，重定向重發驗證信頁面，含收信提示訊息。
            - 信箱無效，重渲染重發驗證信頁面，含錯誤信息及空白 ReVerifyForm 表單。
    """
    if request.method == 'GET':
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

        # 獲取當前域名
        current_site_domain = get_current_site(request).domain
        # 發送驗證信
        email_utils.send_async_email_token(admin, current_site_domain)
        messages.success(request, '驗證信已重新發送，請檢查您的信箱。')
        logger.info(f're-verify email send agine, email:{email[3:]}')
        return redirect('re_verify')
    # 表單驗證失敗，顯示提示訊息
    return render(request, 're-verify.html', {'form': form})
