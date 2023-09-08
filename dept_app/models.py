from datetime import date

from django.db import models
from django.utils import timezone


class Photo(models.Model):
    image = models.ImageField(upload_to='image/', blank=False, null=False)
    upload_data = models.DateField(default=timezone.now)


class Admin(models.Model):
    """ 用戶註冊 """
    username = models.CharField(verbose_name="帳號名", max_length=512)
    password = models.CharField(verbose_name="密碼", max_length=512, null=True)
    email = models.EmailField(verbose_name="信箱", unique=True)
    # 輸出對象時，顯示對象文字

    def __str__(self):
        return self.username




class Department(models.Model):
    """部門表"""
    title = models.CharField(verbose_name="部門", max_length=32, unique=True)

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    """員工表"""
    name = models.CharField(verbose_name="姓名", max_length=16)
    password = models.CharField(verbose_name="密碼", max_length=64)
    birthday = models.DateField(verbose_name="生日", default='2000-01-01')

    def age(self):
        if self.birthday is None:
            return None
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    account = models.DecimalField(verbose_name="帳號餘額", max_digits=10, decimal_places=2, default=0)

    ### 相同變量名字更該數據類型不影響數據
    # create_time = models.DateTimeField(verbose_name="就職時間")
    create_time = models.DateField(verbose_name="就職時間") # 只有年月日沒有時分秒

    # 數據庫中的命令
    # 1.有約束
    #   to  與哪一張表關聯
    #   to_field, 表中的哪一列關聯
    # 2.django自動生成
    #   寫的depart會生成數據列後面加上_id 變成 depart_id
    # 3.部門表被刪除
    # ###3.1 聯級(被約束的一同刪除)刪除
    # depart = models.ForeignKey(to="Department", to_field="id", on_delete=models.CASCADE)
    # ###3.2 置空(有聯級被刪除後就空著)
    depart = models.ForeignKey(verbose_name="部門", to="Department", to_field="id", null=True, blank=True, on_delete=models.SET_NULL)

    # 在django中的命令
    # 加上choices 只能寫元祖中已有的內容
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    # gender = models.SmallIntegerField(verbose_name="性別", choices=gender_choices, unique=True, null=True)
    gender = models.SmallIntegerField(verbose_name="性別", choices=gender_choices)


class PrettyNum(models.Model):
    # 手機號碼用字符串原因是方便搜尋
    mobile = models.CharField(verbose_name="手機號碼", max_length=11)
    price = models.IntegerField(verbose_name="費用", default=0)

    level_choices = (
        (1, "一級"),
        (2, "二級"),
        (3, "三級"),
    )

    level = models.SmallIntegerField(verbose_name="級別", choices=level_choices)

    status_choices = (
        (1, "已佔用"),
        (2, "未占用"),
    )

    status = models.SmallIntegerField(verbose_name="占用", choices=status_choices, default=2)


class Task(models.Model):
    task_choices = (
        (1, "重要"),
        (2, "普通"),
        (3, "閒置"),
    )
    level = models.SmallIntegerField(verbose_name="級別", choices=task_choices, default=1)
    title = models.CharField(verbose_name="標題", max_length=64)
    detail = models.TextField(verbose_name="詳細訊息")

    # 選項可以不選送出，表單會顯示會None
    # user = models.ForeignKey(verbose_name="負責人", to="Admin", to_field="username", null=True, blank=True, on_delete=models.CASCADE)
    # 若需要顯示to_field的對象名稱，請到關聯的表設定(to="Admin")

    # user = models.ForeignKey(verbose_name="負責人", to="Admin", to_field="username", on_delete=models.CASCADE)


