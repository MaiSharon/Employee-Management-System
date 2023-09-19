import uuid
from datetime import timedelta, date
from django.db import models
from django.utils import timezone


class Photo(models.Model):
    image = models.ImageField(upload_to='image/', blank=False, null=False)
    upload_data = models.DateField(default=timezone.now)


class Admin(models.Model):
    """ 用戶註冊 """
    username = models.CharField(verbose_name="用戶名", max_length=512)
    password = models.CharField(verbose_name="密碼", max_length=512, null=True)
    email = models.EmailField(verbose_name="信箱", unique=True)
    email_token = models.UUIDField(verbose_name="電子郵件驗證碼", default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(verbose_name="驗證狀態（已驗證/未驗證）", default=False)
    token_expiration = models.DateTimeField(verbose_name="電子郵件驗證碼期限",default=timezone.now() + timedelta(hours=72))
    is_online = models.BooleanField(verbose_name="用戶在線狀態（已上線/未上線）", default=False)

    def update_token_expiration(self):
        """
        更新用戶的email_token和token_expiration字段。
        這通常在重新發送驗證信時調用。
        """
        self.token_expiration = timezone.now() + timedelta(hours=72)  # 更新驗證期限
        self.email_token = uuid.uuid4()  # 更新驗證碼
        self.save()

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
    birthday = models.DateField(verbose_name="生日", default='2000-01-01')

    def age(self):
        if self.birthday is None:
            return None
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    quota = models.DecimalField(verbose_name="進修額度(美金)", max_digits=10, decimal_places=2, default=0)

    create_time = models.DateField(verbose_name="就職時間") # 只有年月日沒有時分秒

    depart = models.ForeignKey(verbose_name="部門", to="Department", to_field="id", null=True, blank=True, on_delete=models.SET_NULL)

    gender_choices = (
        (1, "男"),
        (2, "女"),
    )

    gender = models.SmallIntegerField(verbose_name="性別", choices=gender_choices)


class MobileNum(models.Model):
    # 手機號碼用字符串原因是方便搜尋
    mobile = models.CharField(verbose_name="手機號碼", max_length=11)
    price = models.IntegerField(verbose_name="電信費", default=0)

    brand_choices = (
        (1, "iPhone 15"),
        (2, "iPhone 15 Pro"),
        (3, "iPhone 14"),
    )

    brand = models.SmallIntegerField(verbose_name="品牌", choices=brand_choices)

    status_choices = (
        (1, "已出借"),
        (2, "未出借"),
    )

    status = models.SmallIntegerField(verbose_name="出借", choices=status_choices, default=2)


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


