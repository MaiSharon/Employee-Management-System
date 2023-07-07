from django.test import TestCase, Client
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from dept_app import models
from dept_app.views.admin import AdminModelForm, AdminEditModelForm


class TestAdminView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # ---創建測試用戶
        cls.valid_username = 'testuser123'
        cls.valid_password = 'Maldifk32l12'
        cls.test_admin = models.Admin.objects.create(username=cls.valid_username, password=make_password(cls.valid_password))

    def setUp(self):
        # ---登入用戶
        self.client = Client()
        session = self.client.session
        session["info"] = {'id': self.test_admin.id, 'name': self.test_admin.username}
        session.save()

    def test_admin_list_view_denied(self):
        self.client.logout()
        # ---未登入時響應的url
        response = self.client.get(reverse('admin_list'))
        self.assertRedirects(response, '/login/')

    def test_admin_list_view(self):
        # ---確認登入此頁面
        response = self.client.get(reverse('admin_list'))
        # print(response.content.decode('utf-8'))  # 輸出HTML並以UTF-8解碼
        # --- 確認頁面響應為200成功
        self.assertEqual(response.status_code, 200)
        # ---響應中是否包含'testuser123'
        self.assertContains(response, 'testuser123')

    def test_admin_create(self):
        user = models.Admin.objects.create(username="hiImteat123", password='Maldifk32l12')
        self.assertEqual(user.username, 'hiImteat123')

    def test_admin_edit_view(self):
        nid = self.test_admin.id
        response = self.client.get(reverse('admin_edit', args=[nid]))

        # 確認有無成功進入此頁面，使用url測試響應狀態
        self.assertEqual(response.status_code, 200)

        # 只能編輯用戶名username
        self.assertContains(response, 'name="username"')
        all_fields = ["username", "password", "confirm_password"]
        for item in all_fields:
            if item != "username":
                # ---確認響應中不包含此字符串(字段)
                self.assertNotContains(response, f"name='{item}'")
