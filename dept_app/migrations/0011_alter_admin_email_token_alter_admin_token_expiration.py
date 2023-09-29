# Generated by Django 4.1.3 on 2023-09-29 13:04

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dept_app', '0010_admin_is_online_alter_admin_email_token_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='email_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True, verbose_name='電子郵件驗證碼'),
        ),
        migrations.AlterField(
            model_name='admin',
            name='token_expiration',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 2, 13, 4, 47, 404678, tzinfo=datetime.timezone.utc), verbose_name='電子郵件驗證碼期限'),
        ),
    ]
