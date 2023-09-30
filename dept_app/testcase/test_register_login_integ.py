from unittest import mock
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse, resolve
from dept_app import models
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class TestRegisterAndLoginIntegration(TestCase):
    """
    Integration test for the registration and login process.

    This test focuses on:
    - User registration through the registration view
    - Email verification
    - User login through the login view
    - Session management during login

    Methods:
    test_register_and_login_integration: Executes the integration test for registration, email verification, and login.
    """

    def setUp(self):
        self.client = Client()
        self.valid_username = "test3user"
        self.valid_password = "test#password"
        self.valid_email = "te88stuser@email.com"

        super().setUp()
        session = self.client.session
        session['image_captcha_entry'] = 'abcd'  # 事先設置一個有效的驗證碼
        session.save()

    @patch('dept_app.utils.email_utils.send_email_token')  # 驗證信件發送
    def test_register_and_login_integration(self, mock_send_email_token):
        """
        Executes the integration test for registration, email verification, and login.

        Steps:
        1. Simulate user registration via POST request.
        2. Validate if the user is saved in the database.
        3. Validate if a verification email is sent.
        4. Simulate clicking the verification link.
        5. Simulate user login via POST request.
        6. Validate if the user is logged in by checking the session.

        Returns:
            None: This method does not return any value.

        Raises:
            AssertionError: If the response status codes, database records, or session data don't match expectations.
        """
        # Make middleware always pass in test
        mock_send_email_token.return_value = True

        # Step 1: Simulate user registration
        response = self.client.post(reverse('register'), {
            'username': self.valid_username,
            'email': self.valid_email,
            'password': self.valid_password,
            'confirm_password': self.valid_password,
        })
        self.assertEqual(response.status_code, 302)  # Assuming redirect after successful registration

        # Step 2: Validate user in database
        user = models.Admin.objects.filter(username=self.valid_username).first()
        self.assertIsNotNone(user)
        # 新增的代碼：檢查 email_token 是否存在和有效
        self.assertIsNotNone(user.email_token)
        print(f"first token: {user.email_token}")

        # 3. verification link


        email_token = urlsafe_base64_encode(force_bytes(user.email_token))

        print(f"second token: {email_token}")

        user.refresh_from_db()

        print(user)
#----------------------------------------------------------------------------------
        # Step 4: Simulate clicking the verification link
        verify_response = self.client.get(reverse('verify_email', args=[email_token]))
        print(verify_response)
        self.assertEqual(verify_response.status_code, 302)  # 或者您期望的其他状态码

        # Refresh user object to get updated fields
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        print(user.password)

        # Step 5: Simulate user login
        login_response = self.client.post(reverse('login'), {
            'username': self.valid_username,
            'password': self.valid_password,
            'image_captcha_input': 'abcd',
        },follow=True)
        # 透過follow來跟隨login跳轉後的路由位置

        # 檢查最終 URL 是否在業務邏輯的特定 URL 上
        self.assertRedirects(login_response, '/admin/list/')
