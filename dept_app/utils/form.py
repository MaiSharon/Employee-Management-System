from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from dept_app import models
from dept_app.utils.bootstrap import BootStrapModelForm

class EmployeeModelForm(BootStrapModelForm):
    """
    表單用於員工管理。負責處理自定義驗證員工的姓名、生日、配額、創建時間、性別和部門。

    Attributes:
        name (CharField): 員工名稱輸入框

    Methods:
        clean_name: 確認用戶名的格式和唯一性
        clean_birthday: 確認生日日期的合理性
        clean_quota:確認配額的數值範圍
        clean_gender: 確認性別選項的正確性
        clean_depart: 確認所選部門的有效性和存在性
    """
    name = forms.CharField(min_length=3, label='用戶名')

    class Meta:
        model = models.UserInfo
        fields = ['name', 'birthday', 'quota', 'create_time', 'gender', 'depart']
        widgets = {
            'create_time': forms.TextInput(attrs={'type': 'date', 'autocomplete': 'off'}),
            'birthday': forms.TextInput(attrs={'type': 'date', 'autocomplete': 'off'})
        }


class MobileModelForm(BootStrapModelForm):
    """
    表單用於手機號碼創建。負責處理自定義驗證手機號碼。

    Attributes:
        mobile (CharField): 手機號碼輸入框

    Methods:
        clean_mobile: 驗證手機號碼的唯一性

    Validators:
        mobile_start: 驗證手機號碼是否以 '09' 開頭。
    """
    mobile_start = RegexValidator(r'^09', '手機號格式錯誤')
    # 報錯提示方式一：正則表達式
    mobile = forms.CharField(
        label='手機號',
        # 0開頭的並且要接3-9之間的數字，\d{8}為之後要接幾個數字。逗號後面為錯誤提示
        # 可以輸入多個錯誤提示
        validators=[RegexValidator(r'\d{8}$', '手機號碼長度錯誤'), mobile_start]
    )

    class Meta:
        model = models.MobileNum
        fields = '__all__'  # 全部字段， exclude = ['level']  # 排除那些字段

    def clean_mobile(self):
        """
        驗證手機號碼符合唯一性。

        Returns:
            str: 驗證通過的手機號碼。

        Raises:
            ValidationError: 手機號碼不符合唯一性。
        """
        txt_mobile = self.cleaned_data['mobile']
        exists = models.MobileNum.objects.filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError('手機號碼已經存在')
        return txt_mobile


class MobileEditModelForm(BootStrapModelForm):
    """
    表單用於編輯手機設備數據。這包括顯示手機的號碼、價格、品牌和出借狀態。

    Attributes:
        mobile (CharField): 顯示當前手機號碼並不可編輯
        price (DecimalField): 手機價格
        brand (CharField): 手機品牌
        status (CharField): 手機的出借狀態（如: 已出借、未出借）

    Methods:
        clean_mobile: 驗證手機號碼的唯一性並排除當前實例
    """
    mobile = forms.CharField(disabled=True, label='mobile')

    class Meta:
        model = models.MobileNum
        fields = ['mobile', 'price', 'brand', 'status']

    def clean_mobile(self):
        """
        驗證手機號碼符合唯一性。排除當前實例以允許更新而不觸發唯一性錯誤。

        Returns:
            str: 驗證通過的手機號碼。

        Raises:
            ValidationError: 手機號碼不符合唯一性。
        """
        txt_mobile = self.cleaned_data['mobile']

        exists = models.MobileNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError('手機號碼已經存在')
        return txt_mobile
