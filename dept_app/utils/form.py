from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from dept_app import models
from dept_app.utils.bootstrap import BootStrapModelForm, BootStrapForm

class EmployeeModelForm(BootStrapModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['name', 'birthday', 'quota', 'create_time', 'gender', 'depart']
        name = forms.CharField(min_length=3, label="用戶名")
        widgets = {
            "create_time": forms.TextInput(attrs={'type': 'date', 'autocomplete': 'off'}),
            "birthday": forms.TextInput(attrs={'type': 'date', 'autocomplete': 'off'})
        }


class MobileModelForm(BootStrapModelForm):
    hi = RegexValidator(r'^09', "手機號格式錯誤")
    # 報錯提示方式一：正則表達式
    mobile = forms.CharField(
        label="手機號",
        # 0開頭的並且要接3-9之間的數字，\d{8}為之後要接幾個數字。逗號後面為錯誤提示
        # 可以輸入多個錯誤提示
        validators=[RegexValidator(r'\d{8}$', "手機號碼長度錯誤"), hi]
    )

    class Meta:
        model = models.MobileNum
        fields = "__all__"  # 全部字段
        # exclude = ["level"]  # 排除那些字段

    def clean_mobile(self):
        txt_mobile = self.cleaned_data["mobile"]
        exists = models.MobileNum.objects.filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手機號碼已經存在")

        # 驗證通過，用戶輸入的值返回
        return txt_mobile


class MobileEditModelForm(BootStrapModelForm):
    mobile = forms.CharField(disabled=True, label="mobile")

    class Meta:
        model = models.MobileNum
        fields = ["mobile", "price", "brand", "status"]

    def clean_mobile(self):
        txt_mobile = self.cleaned_data["mobile"]

        exists = models.MobileNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手機號碼已經存在")

        return txt_mobile

