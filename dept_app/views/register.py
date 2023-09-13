from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django import forms
from django.shortcuts import render, redirect

from dept_app import models
from dept_app.utils import email_utils
from dept_app.utils.bootstrap import BootStrapModelForm, BootStrapForm


class AdminModelForm(BootStrapModelForm):
    """
    表單用於管理員註冊，包括用戶名、電子郵件和密碼。
    這個表單還進行了密碼和用戶名的自定義驗證。
    """
    confirm_password = forms.CharField(
        label="確認密碼",
        widget=forms.PasswordInput(render_value=True),  # 當密碼不一致不清空，預設會自動清空# *****
    )

    class Meta:
        model = models.Admin
        fields = ["username", "email", "password"]
        widgets = {
            'username': forms.TextInput(attrs={'render_value': True}),
            'email': forms.EmailInput(attrs={'render_value': True}),
            "password": forms.PasswordInput(attrs={'render_value': True}),  # 當密碼不一致不清空，預設會自動清空# *****
        }


    def clean_username(self):
        """ 檢查用戶名是否只包含字母、數字、下劃線和點、用戶名不可重複 """
        username = self.cleaned_data.get("username")
        if not all(char.isalnum() or char in {'_', '.'} for char in username):
            raise ValidationError("用戶名只能包含字母、數字、下劃線和點")

        if not (any(char.isdigit() for char in username) and any(char.isalpha() for char in username)):
            raise ValidationError("用戶名必須包含至少一個字母和一個數字")

        if len(username) < 8 or len(username) > 16:
            raise ValidationError("用戶名必須在8到16個字符之間")

        exists = models.Admin.objects.filter(username=username).exists()
        if exists:
            raise ValidationError(f"{username} 此用戶名已經存在")

        return username

    def clean_password(self):
        """ 檢查密碼是否符合長度8~64、不含空格、含至少1個特殊字符 """
        password = self.cleaned_data.get("password")

        # 最小長度檢查
        if len(password) < 8:
            raise ValidationError("密碼長度必須至少為8個字符")

        if len(password) >= 65:
            raise ValidationError("密碼長度不可超過64個字符")

        if ' ' in password:
            raise ValidationError("密碼不能包含空格")

        if not any(char in "!@#$%^&*()-+_=<>?/[]" for char in password):
            raise ValidationError("密碼必須包含至少一個特殊字符")

        # Django內建的密碼強度檢查，已含最小長度檢查不可<8
        validate_password(password, self.instance)
        return password

    def clean_confirm_password(self):
        """ 檢查密碼確認是否一致、不可為空 """
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password is None:
            return confirm_password

        if password != confirm_password:
            raise ValidationError("密碼不一致")

        return confirm_password

    def clean_email(self):
        """ 檢查信箱驗證狀態 """
        email = self.cleaned_data.get("email")
        if models.Admin.objects.filter(email=email, is_verified=False).exists():
            raise ValidationError("請至信箱收信完成驗證")
        elif models.Admin.objects.filter(email=email, is_verified=True).exists():
            raise ValidationError("此信箱已註冊，請直接登入。")
        else:
            # 此信箱未註冊
            return email

import logging

logger = logging.getLogger(__name__)


def admin_add(request):
    """
    處理管理員賬戶的創建。
    - GET請求：顯示空的註冊表單。
    - POST請求：驗證表單數據，創建新的管理員賬戶。
    """

    if request.method == "GET":
        form = AdminModelForm()
        return render(request, "register.html", {"form": form})

    # 處理POST請求
    form = AdminModelForm(data=request.POST)
    logger.info("Received GET request for admin registration.")
    if form.is_valid():
        admin = form.save(commit=False)
        admin.password = make_password(form.cleaned_data["password"])
        admin.save()

        # 發送驗證郵件
        email_utils.send_email_token(request, admin)
        messages.success(request, '驗證郵件已發送，請檢查您的信箱。')

        # 記錄成功創建的管理員賬戶
        logger.info(f"Admin account created: {admin.username}, Email: [REDACTED]")
        return redirect("register")

    # 記錄失敗的註冊嘗試（敏感信息已脫敏）
    sanitized_errors = {k: "[REDACTED]" if k in ["password", "email"] else v for k, v in form.errors.items()}
    logger.warning(f"Failed admin account creation attempt: {sanitized_errors}")
    # 表單驗證失敗，顯提示信息
    return render(request, "register.html", {"form": form})



def verify_email(request, token):
    """
    驗證用戶的電子郵件。
    這個函數會解碼URL中的驗證碼，並查找對應的Admin對象。
    如果驗證成功，它會更新Admin對象的狀態。
    """
    try:
        # 解碼從URL中獲取的驗證碼
        email_token = force_str(urlsafe_base64_decode(token))
        if None != email_token:
            logger.info(f"Attempting to decode email token: {token[:5]}")
        # 查找對應的Admin對象
        admin = models.Admin.objects.get(email_token=email_token)

    except ObjectDoesNotExist:
        # 若無對應的Admin對象，可能是已驗證或無效驗證碼都到重新驗證頁面
        messages.success(request, '無效驗證碼或已驗證成功，請重發認證信或登入。')
        logger.warning(f"Failed email_token: is None")
        return redirect('re_verify')

    if timezone.now() > admin.token_expiration:
        # 若驗證碼是否過期，到重新驗證輸入信箱頁面
        messages.success(request, '驗證碼已過期，請重新發送認證信。')
        logger.warning(f"Token for Admin object with email_token: {email_token[:5]} has expired.")
        return redirect('re_verify')

    # 若驗證成功，更新Admin對象的狀態並保存
    admin.is_verified = True
    admin.email_token = None
    admin.save()
    logger.info(f"Admin object with Username: {admin.username} is verified.")
    # 直接登入，進入管理員列表頁面
    return redirect('admin_list')


class ReVerifyForm(BootStrapForm):
    email = forms.EmailField(label='請輸入您的信箱')

    def clean_email(self):
        """ 檢查信箱是否已註冊並且未驗證 """
        email = self.cleaned_data.get("email")
        try:
            admin = models.Admin.objects.get(email=email)
        except models.Admin.DoesNotExist:
            raise ValidationError("此信箱未註冊，請重新輸入。")

        if admin.is_verified:
            raise ValidationError("您已驗證成功，請直接登入。")

        return email

def re_verify(request):
    """ 重發驗證信 """

    # 輸入信箱
    if request.method == "GET":
        form = ReVerifyForm
        return render(request, 're-verify.html', {'form': form})

    form = ReVerifyForm(data=request.POST)
    if form.is_valid():
        email = form.cleaned_data.get("email")
        admin = models.Admin.objects.get(email=email, is_verified=False)

        # 更新驗證碼過期時間
        admin.update_token_expiration()
        admin.save()

        # 重新發送驗證信
        email_utils.send_email_token(request, admin)
        messages.success(request, '驗證郵件已重新發送，請檢查您的信箱。')
        return redirect('re-verify')
    # 表單驗證失敗，顯示提示訊息
    return render(request, 're-verify.html', {'form': form})

