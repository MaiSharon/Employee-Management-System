from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import forms
from dept_app import models
from dept_app.utils.bootstrap import BootStrapForm
from dept_app.utils.image_code import check_code


class LoginForm(BootStrapForm):
    username = forms.CharField(
        label="用戶名",
        widget=forms.TextInput,  # 被BootStrapForm裡的樣式屬性設定控制
        required=True
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(render_value=True),  # 輸入錯密碼但密碼仍保留 # 被BootStrapForm裡的樣式屬性設定控制，若無繼承則如下行
        # widget=forms.PasswordInput(attrs={"class": "form-control form-control-sm"})
        required=True

    )
    user_code = forms.CharField(
        label="圖片驗證碼",
        widget=forms.TextInput,  # 目前樣式屬性繼承自BootStrapForm，若無繼承則如下行
        # widget=forms.PasswordInput(attrs={"class": "form-control form-control-sm"})
        required=True

    )
    #
    # def clean_password(self):
    #     pwd = self.cleaned_data.get("password")
    #     return md5(pwd)


def login(request):
    """ 登錄功能 """
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    form = LoginForm(data=request.POST)

    # 驗證表單是否有效
    if form.is_valid():

        # 檢查驗證碼是否過期
        if 'image_code' not in request.session:
            form.add_error("user_code", "驗證碼已過期，請輸入新驗證碼。")
            return render(request, "login.html", {"form": form})

        # 驗證圖片驗證碼
        user_input_code = form.cleaned_data.pop('user_code')  # 從字典中先移除圖片驗證碼
        code = request.session.get('image_code', "")
        if user_input_code.upper() != code.upper():
            form.add_error("user_code", "驗證碼錯誤")
            return render(request, "login.html", {"form": form})

        # 查找並驗證管理員對象
        # 等同下行models.Admin.objects.filter(username=form.cleaned_data["username"], password=form.cleaned_data["password"]).first()
        admin_object = models.Admin.objects.filter(username=form.cleaned_data["username"]).first()
        if not admin_object:
            """不存在的用戶出現的錯誤提示"""
            form.add_error("username", "用戶名錯誤")
            return render(request, "login.html", {"form": form})

        # 使用 check_password 驗證密碼
        if not check_password(form.cleaned_data["password"], admin_object.password):
            form.add_error("password", "密碼錯誤")
            return render(request, "login.html", {"form": form})


        # 網站會先隨機生成字符串，使用者來訪後給使用者生成的隨機字符串，登入成功再寫入session(在資料庫裡叫做django_session)
        # 用戶訊息寫入到session中，也就是session概念中特定儲存空間的小格子裡面
        request.session["info"] = {'id': admin_object.id, 'name': admin_object.username}
        # 重新设置session的超时时间,這段時間內來訪者的session不會刪除可以持續保持登入狀態
        request.session.set_expiry(60 * 60 * 24)

        return redirect("/admin/list")

    return render(request, "login.html", {"form": form})


def logout(request):
    """ 登出功能 """
    request.session.clear()
    return redirect("/login/")


from io import BytesIO

def image_code(request):
    """ 生成图片验证码 """
    # 调用pillow函数,生成图片
    img, code_string = check_code()

    # 登入時的圖片校驗
    ## 每一位來訪者的session給予圖片驗證碼答案
    request.session["image_code"] = code_string
    ## 設定時間定期刷新圖片驗證碼
    request.session.set_expiry(60)

    # 将图片保存到内存
    stream = BytesIO()  # 相當於創建了個文件
    img.save(stream, 'png')  # 圖片寫入內存文件中
    return HttpResponse(stream.getvalue())
