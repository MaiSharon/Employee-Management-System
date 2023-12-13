import logging

from django import forms
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_http_methods

from dept_app import models
from dept_app.utils.bootstrap import BootStrapForm
from dept_app.utils.image_code.image_code import check_code

logger = logging.getLogger(__name__)

class LoginForm(BootStrapForm):
    """
    表單用於用戶登入。負責處理自定義驗證用戶名、密碼和圖片驗證碼。

    Attributes:
        username (CharField): 用戶名輸入框
        password (CharField): 密碼輸入框
        image_captcha_input (CharField): 圖片驗證碼輸入框

    Methods:
        clean_username: 確認用戶是否存在。
        clean_password: 確認密碼是否跟用戶名匹配。
    """
    username = forms.CharField(
        label='用戶名',
        widget=forms.TextInput,
        required=True
    )
    password = forms.CharField(
        label='密碼',
        widget=forms.PasswordInput(render_value=True),  # 輸入錯密碼但密碼仍保留
        required=True
    )
    image_captcha_input = forms.CharField(
        label='圖片驗證碼',
        widget=forms.TextInput,
        required=True
    )

    def clean_username(self):
        """
        驗證用戶名是否存在。

        Returns:
            str: 驗證通過的用戶名。

        Raises:
            ValidationError: 用戶名不存在。
        """
        username = self.cleaned_data.get('username')
        admin_object = models.Admin.objects.filter(username=username, is_verified=True).exists()
        if admin_object is False:
            raise ValidationError('用戶不存在')
        return username

    def clean_password(self):
        """
        驗證密碼是否跟用戶名匹配。

        Returns:
            str: 驗證通過的密碼。

        Raises:
            ValidationError: 密碼不匹配。
        """
        password = self.cleaned_data.get('password','')
        admin_object = models.Admin.objects.filter(username=self.cleaned_data.get("username")).first()
        if admin_object:
            if not check_password(password, admin_object.password):
                raise ValidationError('密碼錯誤')
        return password

@require_http_methods(['GET', 'POST'])
def login(request):
    """
    處理用戶登入請求。

    - GET: 返回空白登入表單（LoginForm）。
    - POST: 處理提交的登入數據以執行登入。

    Steps for GET: 創建並渲染空的 LoginForm。

    Steps for POST:
        1. 驗證圖片驗證碼是否過期。
            1.1. 若過期，提示用戶重新整理並重渲染表單，日誌記錄。
        2. 驗證用戶輸入的圖片驗證碼。
            2.2. 若錯誤，提示錯誤信息並重渲染表單，日誌記錄
        3. 驗證登入表單。
        4. 若驗證成功
            4.1. 儲存用戶信息到 session。
            4.2. 設定 session 到期時間。
            4.3. 重定向到管理員列表頁面。
        5. 若驗證失敗
            5.1. 記錄操作，顯示錯誤信息並重渲染表單。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。

    Returns HttpResponse:
        - GET: 渲染過的登入頁面，含空白 LoginForm。
        - POST:
            - 成功，重定向管理員頁面，並儲存用戶信息到 session。
            - 失敗，重渲染登入頁面，含錯誤訊息及空白 LoginForm。
    """
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        # 檢查圖片驗證碼是否過期、若過期請使用者重新整理
        if 'image_captcha_entry' not in request.session:
            form.add_error('image_captcha_input','驗證碼已過期')
            logger.warning('image captcha expiration')
            return render(request, 'login.html', {'form': form})

        # 檢查使用者輸入的圖片驗證碼是否與session中儲存的驗證碼相符
        user_image_captcha_input = form.cleaned_data.get('image_captcha_input')
        code = request.session.get('image_captcha_entry','')  # ''用意: 若輸入為空 返回空字串(預設返回None會導致.upper()報錯)
        if user_image_captcha_input.upper() != code.upper():
            form.add_error('image_captcha_input', '驗證碼錯誤')
            logger.warning('image captcha user input wrong')
            return render(request, 'login.html', {'form': form})

        # 使用者登入成功，將用戶信息儲存到session
        # 使用者來訪後網站將生成的隨機字符串，若用戶登入成功此隨機字符串會寫入到session中(Web 伺服器的內存)之後儲存(在資料庫裡叫做django_session)

        # 為了後續session再調用
        admin_object = models.Admin.objects.filter(username=form.cleaned_data['username']).first()

        # 'info' 這個session變數將在用戶身份驗證時使用
        request.session['info'] = {'id': admin_object.id, 'name': admin_object.username}
        # 設定session到期時間為24小時，60秒*60次*24次 -> 24小時
        request.session.set_expiry(60 * 60 * 24)
        return redirect('admin_list')

    # 日誌顯示登入錯誤用戶名與脫敏密碼
    sanitized_errors = {k: '[REDACTED]' if k in ['password'] else v for k, v in form.errors.items()}
    logger.warning(f'Failed admin login attempt: {sanitized_errors}')
    return render(request, 'login.html', {'form': form})

@require_GET
def logout(request):
    """
    處理用戶登出請求。

    - GET: 清空 session 並重定向到登入頁面。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。

    Returns HttpResponse:
        - GET: 重定向到登入頁面。
    """
    request.session.clear()
    return redirect('login')


from io import BytesIO

@require_GET
def image_code(request):
    """
    處理圖片驗證碼生成請求。

    - GET: 生成新的圖片驗證碼，並將其保存在用戶的 session 中。

    Steps for GET:
        1. 使用 check_code 方法生成驗證碼圖片、對應的驗證碼字符串。
        2. 將驗證碼字符串存儲到 session，並設置 60 秒過期。
        3. 將驗證碼圖片保存到內存中，並以 'image/png' 格式返回。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。

    Returns HttpResponse:
        - GET: 驗證碼圖片，內容類型為 'image/png'。
    """
    # 生成圖片、生成驗證碼
    img, code_string = check_code()

    # 驗證碼儲存到session
    request.session['image_captcha_entry'] = code_string
    # 定期刷新圖片驗證碼
    request.session.set_expiry(60)

    # 圖片保存到內存
    stream = BytesIO()  # 相當於創建了個文件
    img.save(stream, 'png')  # 圖片寫入內存文件中
    img_show = stream.getvalue()  # 取圖片
    return HttpResponse(img_show, content_type='image/png')
