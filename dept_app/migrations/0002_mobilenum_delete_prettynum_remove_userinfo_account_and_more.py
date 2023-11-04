# Generated by Django 4.1.3 on 2023-11-04 15:32

import dept_app.models
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dept_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobileNum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(max_length=11, verbose_name='手機號碼')),
                ('price', models.IntegerField(default=0, verbose_name='電信費')),
                ('brand', models.SmallIntegerField(choices=[(1, 'iPhone 15'), (2, 'iPhone 15 Pro'), (3, 'iPhone 14')], verbose_name='品牌')),
                ('status', models.SmallIntegerField(choices=[(1, '已出借'), (2, '未出借')], default=2, verbose_name='出借')),
            ],
        ),
        migrations.DeleteModel(
            name='PrettyNum',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='account',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='password',
        ),
        migrations.AddField(
            model_name='admin',
            name='email_send_time',
            field=models.DateTimeField(default=dept_app.models.one_minute_from_now, help_text='設定電子郵件發送的時間點，預設為創建記錄的當下時間加一分鐘。', verbose_name='寄信期限'),
        ),
        migrations.AddField(
            model_name='admin',
            name='email_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True, verbose_name='電子郵件驗證碼'),
        ),
        migrations.AddField(
            model_name='admin',
            name='is_online',
            field=models.BooleanField(default=False, verbose_name='用戶在線狀態（已上線/未上線）'),
        ),
        migrations.AddField(
            model_name='admin',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='驗證狀態（已驗證/未驗證）'),
        ),
        migrations.AddField(
            model_name='admin',
            name='token_expiration',
            field=models.DateTimeField(default=dept_app.models.three_days_from_now, verbose_name='電子郵件驗證碼期限'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='quota',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='進修額度(美金)'),
        ),
        migrations.AlterField(
            model_name='admin',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='信箱'),
        ),
        migrations.AlterField(
            model_name='admin',
            name='username',
            field=models.CharField(max_length=512, verbose_name='用戶名'),
        ),
    ]
