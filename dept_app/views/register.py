from django.forms import ModelForm
from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from dept_app import models



class AdminModelForm(ModelForm):
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


    def clean_username(self):
        """ 驗證用戶名是否只包含字母、數字、下劃線和點 """
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
        return render(request, "register.html", {"form": form, "title": "新增管理員"})

    form = AdminModelForm(data=request.POST)
    if form.is_valid():
        admin = form.save(commit=False)
        admin.password = make_password(form.cleaned_data["password"])
        admin.save()
        return redirect("/admin/list/")

