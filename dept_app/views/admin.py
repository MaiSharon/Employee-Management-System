from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from dept_app import models
from dept_app.utils.pagination import Pagination
from dept_app.utils.bootstrap import BootStrapModelForm


def admin_list(request):
    """ 管理員 """

    #  已經使用中間件校驗並登入了，可直接抓取數據
    ## "info"這個名稱不是預設，是在account.py中login中定義的(session特定空間小格子)
    #### "id"、"name"也是在是在account.py中login中定義的
    # info_dict = request.session.get("info", {})
    # print(info_dict["id"])
    # print(info_dict["name"])
    ##假如沒登入，返回到登入頁面
    # if 'id' not in request.session.get("info", {}):
    #     return redirect("/login")

    search_dict = {}
    search = request.GET.get("search", "")  # 預設為空字串，讓input不出現None保持乾淨空的
    if search:  # 0.2.1 True 將會把獲取值新增到字典
        search_dict["username__contains"] = search  # 找出 username 欄位中包含特定字串的所有對象"。contains 是一種查詢類型

    queryset = models.Admin.objects.filter(**search_dict)

    page_object = Pagination(request, queryset)

    context = {
        "search": search,
        "queryset": page_object.page_queryset,  # 分完頁的數據
        "page_string": page_object.html(),  # 頁碼


    }

    return render(request, "admin_list.html", context)


class AdminModelForm(BootStrapModelForm):
    """  """
    confirm_password = forms.CharField(
        label="確認密碼",
        widget=forms.PasswordInput(render_value=True),  # 當密碼不一致不清空，預設會自動清空# *****
    )

    class Meta:
        model = models.Admin
        fields = ["username", "password", "confirm_password"]  #
        widgets = {
            "password": forms.PasswordInput(render_value=True),  # 當密碼不一致不清空，預設會自動清空# *****
        }

    # --- 用戶名驗證。數據字段設定(....unique=True)
    # 即便沒有鉤子驗證規則，輸入已有用戶名會出現"這個 帳號名 在 Admin 已經存在。"
    def clean_username(self):
        username = self.cleaned_data.get("username")
        # 檢查用戶名是否只包含字母、數字、下劃線和點
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
        password = self.cleaned_data.get("password")
        if len(password) >= 25:
            raise ValidationError("密碼長度不可超過24個字符")
        if ' ' in password:
            raise ValidationError("密碼不能包含空格")
        validate_password(password, self.instance)
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password is None:  # 相較self.errors.get("password")更節省資源
            return confirm_password

        if password != confirm_password:
            raise ValidationError("密碼不一致")

        return confirm_password


def admin_add(request):
    title = "新增管理員"
    if request.method == "GET":
        form = AdminModelForm()
        return render(request, "change.html", {"form": form, "title": "新增管理員"})

    form = AdminModelForm(data=request.POST)
    if form.is_valid():
        admin = form.save(commit=False)
        admin.password = make_password(form.cleaned_data["password"])
        admin.save()
        return redirect("/admin/list/")

    return render(request, "change.html", {"form": form, "title": title})


class AdminResetModelForm(BootStrapModelForm):
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

    # 不跟之前的密碼一樣
    return render(request, "change.html", {"title": title, "form": form})


class AdminEditModelForm(BootStrapModelForm):
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


def admin_delete(request, nid):
    """ 刪除管理員 """
    models.Admin.objects.filter(id=nid).delete()

    return redirect("/admin/list/")

