# Generated by Django 4.1.3 on 2023-09-19 03:47

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dept_app', '0009_rename_prettynum_mobilenum_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='is_online',
            field=models.BooleanField(default=False, verbose_name='用戶在線狀態（已上線/未上線）'),
        ),
        migrations.AlterField(
            model_name='admin',
            name='email_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='電子郵件驗證碼'),
        ),
        migrations.AlterField(
            model_name='admin',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='驗證狀態（已驗證/未驗證）'),
        ),
        migrations.AlterField(
            model_name='admin',
            name='token_expiration',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 22, 3, 47, 9, 399307, tzinfo=datetime.timezone.utc), verbose_name='電子郵件驗證碼期限'),
        ),
    ]
