from django.test import TestCase, Client
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from dept_app import models
from dept_app.views.admin import AdminEditModelForm


class TestAdminModelForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        # ---創建測試用戶
        cls.valid_username = 'testuser123'
        cls.valid_password = 'Maldifk32l12'
        cls.test_admin = models.Admin.objects.create(username=cls.valid_username,
                                                     password=make_password(cls.valid_password))

    def setUp(self):
        # ---登入用戶
        self.client = Client()
        session = self.client.session
        session["info"] = {'id': self.test_admin.id, 'name': self.test_admin.username}
        session.save()



    def test_admin_edit_form(self):
        # ---輸入重複用戶名送出時出現錯誤
        form = AdminEditModelForm(data={'username': self.valid_username})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'][0], f"{self.valid_username} 此用戶名已經存在")

        # 輸入不存在的id，確定執行重定像
        response = self.client.get(reverse('admin_edit', args=[3]))
        self.assertRedirects(response, '/admin/list/')
