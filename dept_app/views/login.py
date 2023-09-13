from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import forms
from dept_app import models
from dept_app.utils.bootstrap import BootStrapForm
from dept_app.utils.image_code.image_code import check_code
import logging

logger = logging.getLogger(__name__)

class LoginForm(BootStrapForm):
    """
    表單用於用戶登入，包括用戶名、密碼、圖片驗證碼。
    用戶名和密碼的自定義驗證，不包含圖片驗證碼的驗證。
    """
    username = forms.CharField(
        label="用戶名",
        widget=forms.TextInput,
        required=True
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(render_value=True),  # 輸入錯密碼但密碼仍保留
        required=True
    )
    image_captcha_input = forms.CharField(
        label="圖片驗證碼",
        widget=forms.TextInput,
        required=True
    )

    def clean_username(self):
        """檢查用戶是否存在"""
        username = self.cleaned_data.get("username")
        admin_object = models.Admin.objects.filter(username=username).first()
        if admin_object is None:
            raise ValidationError("用戶不存在")
        return username

    def clean_password(self):
        """檢查密碼是否跟用戶名匹配"""
        password = self.cleaned_data.get("password")
        admin_object = models.Admin.objects.filter(username=self.cleaned_data.get("username")).first()
        if not check_password(password, admin_object.password):
            raise ValidationError("密碼錯誤")
        return password


def login(request):
    """
    處理用戶登入。
    - GET請求：顯示空的註冊表單。
    - POST請求：驗證表單數據、圖片驗證碼的自定義驗證，登入。
    """
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        # 檢查圖片驗證碼是否過期
        # 若過期請使用者重新整理
        if 'image_captcha_entry' not in request.session:
            form.add_error("image_captcha_input","驗證碼已過期，請重新整理頁面。")
            logger.warning("image captcha expiration")
            return render(request, "login_old.html", {"form": form})

        # 檢查使用者輸入的圖片驗證碼是否與session中儲存的驗證碼相符
        user_image_captcha_input = form.cleaned_data.get('image_captcha_input')  # 從字典中先移除圖片驗證碼
        code = request.session.get('image_captcha_entry',"")  # ""用意: 若輸入為空 返回空字串(預設返回None)，後續安全執行.upper()
        if user_image_captcha_input.upper() != code.upper():
            form.add_error("image_captcha_input", "驗證碼錯誤")
            logger.warning("image captcha user input wrong")
            return render(request, "login.html", {"form": form})

        # 使用者登入成功，將用戶信息儲存到session
        # 使用者來訪後網站將生成的隨機字符串，若用戶登入成功此隨機字符串會寫入到session中(Web 伺服器的內存)之後儲存(在資料庫裡叫做django_session)
        admin_object = models.Admin.objects.filter(username=form.cleaned_data['username']).first()
        # 'info' 這個session變數將在用戶身份驗證時使用
        request.session["info"] = {'id': admin_object.id, 'name': admin_object.username}

        # 設定session到期時間為24小時
        request.session.set_expiry(60 * 60 * 24) # 60秒*60次*24次 -> 24小時
        return redirect("/admin/list")

    # 日誌顯示登入錯誤用戶名與脫敏密碼
    sanitized_errors = {k: "[REDACTED]" if k in ["username", "password"] else v for k, v in form.errors.items()}
    logger.warning(f"Failed admin login attempt: {sanitized_errors}")
    return render(request, "login.html", {"form": form})


def logout(request):
    """登出"""
    request.session.clear()
    return redirect("/login/")


from io import BytesIO

def image_code(request):
    """生成圖片驗證碼"""
    # 生成圖片、生成驗證碼
    img, code_string = check_code()

    # 驗證碼儲存到session
    request.session["image_captcha_entry"] = code_string
    # 定期刷新圖片驗證碼
    request.session.set_expiry(60)

    # 圖片保存到內存
    stream = BytesIO()  # 相當於創建了個文件
    img.save(stream, 'png')  # 圖片寫入內存文件中
    img_show = stream.getvalue()  # 取圖片
    return HttpResponse(img_show, content_type='image/png')

