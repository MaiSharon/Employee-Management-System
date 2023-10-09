from django.forms import ModelForm
from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_GET, require_http_methods

from dept_app import models
from dept_app.utils.pagination import Pagination
from dept_app.utils.validate_utils import validate_search

import logging

logger = logging.getLogger(__name__)

@require_GET
def admin_list(request):
    """
    展示管理員列表並分頁、搜尋功能。

    Usage:
    - GET: 展示管理員列表、搜尋。
    """
    # 接收用戶輸入搜尋內容
    search_input = request.GET.get("search", "").strip()  # 獲取 'search' 參數的值，若無則為空字串。去除頭尾空格
    # 驗證搜尋輸入內容
    is_valid_search_input = validate_search(search_input)

    # 搜尋或返回所有數據
    all_queryset_or_search_result = models.Admin.objects.filter(username__icontains=is_valid_search_input)

    # 分頁處理
    page_object = Pagination(request, queryset=all_queryset_or_search_result, page_size=15)

    context = {
        "search": is_valid_search_input,
        "queryset": page_object.page_queryset,  # 分完頁的數據
        "page_string": page_object.generate_html(),  # 頁碼
        "page_title": "Administrators",
    }

    return render(request, "admin_list.html", context)



class AdminResetModelForm(ModelForm):
    confirm_password = forms.CharField(
        label="確認密碼",
        widget=forms.PasswordInput(render_value=True)  # 密碼不一致不清空，預設會自動清空# *****
    )

    class Meta:
        model = models.Admin
        fields = ["password", "confirm_password"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) >= 25:
            raise ValidationError("密碼長度不可超過24個字符")
        if ' ' in password:
            raise ValidationError("密碼不能包含空格")
        validate_password(password, self.instance)
        return password

    # --- 確認用戶輸入的兩次密碼是一致的
    def clean_confirm_password(self):

        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password is None:  # 相較self.errors.get("password")更節省資源
            return confirm_password

        if password != confirm_password:
            raise ValidationError("密碼不一致")

        return confirm_password

@require_http_methods(["GET", "POST"])
def admin_reset(request, nid):
    """ 重設密碼 """
    row_object = models.Admin.objects.filter(id=nid).first()
    title = f"重設密碼 - {row_object.username}"

    if not row_object:  # 防止用戶在網址輸入不存在的列表
        return redirect("/admin/list/")

    if request.method == "GET":
        form = AdminResetModelForm()
        return render(request, "change.html", {"title": title, "form": form})

    form = AdminResetModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        admin = form.save(commit=False)  # 获取表单数据但不保存
        admin.password = make_password(form.cleaned_data["password"])
        admin.save()
        return redirect("/admin/list/")

    return render(request, "change.html", {"title": title, "form": form})


class AdminEditModelForm(ModelForm):
    class Meta:
        model = models.Admin
        fields = ["username"]

    # --- 用戶名驗證。數據字段設定(....unique=True)
    # 即便沒有鉤子驗證規則，輸入已有用戶名會出現"這個 帳號名 在 Admin 已經存在。"
    def clean_username(self):
        username = self.cleaned_data.get("username")
        # 檢查用戶名是否只包含字母、數字、下劃線和點
        if not all(char.isalnum() or char in {'_', '.'} for char in username):
            raise ValidationError("用戶名只能包含字母、數字、下劃線和點")

        # 檢查用戶名是否包含至少一個字母和一個數字
        if not (any(char.isdigit() for char in username) and any(char.isalpha() for char in username)):
            raise ValidationError("用戶名必須包含至少一個字母和一個數字")

        # 檢查用戶名的長度
        if len(username) < 8 or len(username) > 16:
            raise ValidationError("用戶名必須在8到16個字符之間")

        # 檢查用戶名是否已存在
        exists = models.Admin.objects.filter(username=username).exists()
        if exists:
            raise ValidationError(f"{username} 此用戶名已經存在")

        return username


def admin_edit(request, nid):
    title = "編輯管理員"
    row_object = models.Admin.objects.filter(id=nid).first()

    if not row_object:  # 防止用戶在網址輸入不存在的列表
        # return render(request, "error.html", {"msg": "數據不存在"})
        return redirect("/admin/list/")

    if request.method == "GET":
        form = AdminEditModelForm(instance=row_object)
        return render(request, "change.html", {"title": title, "form": form})

    form = AdminEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")

    return render(request, "change.html", {"title": title, "form": form})

