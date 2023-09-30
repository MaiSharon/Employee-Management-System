from unittest.mock import patch, Mock, MagicMock

from django.contrib.auth.hashers import make_password
from django.test import TestCase, RequestFactory
from dept_app.middleware.auth import AuthMiddleware
from dept_app.views import login


class LoginFormTest(TestCase):
    """
    Test cases for validating the LoginForm functionality.

    Main Features:
    - 用戶名的清理和驗證
    - 密碼的清理和驗證
    - 登錄視圖的 HTTP GET 和 POST(含自定義中間件) 方法
    - 注銷功能

    Attributes:
    factory (RequestFactory): 用於創建模擬請求對象的工廠。

    Methods:
    test_clean_username：驗證 LoginForm 中用戶名字段的清理。
    test_clean_password：驗證 LoginForm 中密碼字段的清理。
    test_login_view_GET：測試登錄視圖的 GET 方法。
    test_login_view_POST_valid：使用有效數據(含自定義中間件)測試登錄視圖的 POST 方法。
    test_logout：測試注銷功能。
    """
    def setUp(self):
        """Set up the test environment."""
        self.factory = RequestFactory()

    @patch('dept_app.models.Admin.objects.filter')
    def test_clean_username(self, mock_filter):
        mock_admin = Mock()
        mock_filter.return_value.first.return_value = mock_admin
        form = login.LoginForm(data={'username': 'testuser', 'password': 'testpassword', 'image_captcha_input': '1234'})
        form.is_valid()
        self.assertEqual(form.clean_username(), 'testuser')

    @patch('dept_app.models.Admin.objects.filter')
    def test_clean_password(self, mock_filter):
        mock_admin = Mock()
        mock_admin.password = make_password('testpassword')
        mock_filter.return_value.first.return_value = mock_admin
        with patch('django.contrib.auth.hashers.check_password') as mock_check_password:
            mock_check_password.return_value = True
            form = login.LoginForm(data={'username': 'testuser', 'password': 'testpassword', 'image_captcha_input': '1234'})
            is_valid = form.is_valid()
            self.assertTrue(is_valid)
            if is_valid:
                self.assertEqual(form.clean_password(), 'testpassword')

    def test_login_view_GET(self):
        request = self.factory.get('/login/')
        response = login.login(request)
        self.assertEqual(response.status_code, 200)

    @patch('dept_app.models.Admin.objects.filter')
    def test_login_view_POST_valid(self, mock_filter):
        """
        用有效數據測試登錄視圖的 POST 方法。

        Steps：
        1. 模擬 Admin 對象配置特定屬性（id、用戶名和密碼） 。
        2. 模擬 POST 請求輸入用戶名、密碼和圖像驗證碼 。
        3. 將自定義身份驗證中間件 AuthMiddleware 應用於請求。
        4. 模擬 session 中存在 'image_captcha_entry' (圖片驗證碼) 和 'set_expiry' (到期時間 )。
        5. 模擬 Django 的 auth 中的 check_password 函數。
        6. 調用登入視圖函數。
        7. 驗證 HTTP 響應狀態碼是否為 302

        參數：
            mock_filter (MagicMock)：Admin 模型的模擬過濾方法。

        Returns：
            無：此方法不返回任何值。

        Raises：
            AssertionError：如果響應狀態碼與預期值不匹配（狀態碼: 302）。
        """
        # Mocking Admin instance
        mock_admin = Mock()
        mock_admin.id = 1
        mock_admin.username = 'testuser'
        mock_admin.password = make_password('testpassword')
        mock_filter.return_value.first.return_value = mock_admin

        # Mocking a POST request
        request = self.factory.post('/login/', data={'username': 'testuser', 'password': 'testpassword',
                                                     'image_captcha_input': '1234'})

        # Applying custom middleware
        middleware = AuthMiddleware(get_response=Mock())
        middleware.process_request(request)

        # Mocking the session
        request.session = MagicMock()
        request.session.__contains__.return_value = True  # 模擬 'image_captcha_entry' 在 session 中
        request.session.set_expiry = MagicMock()  # 模擬 'set_expiry'
        request.session.get.return_value = '1234'  # 模擬 get 方法返回 '1234'

        with patch('django.contrib.auth.hashers.check_password') as mock_check_password:
            mock_check_password.return_value = True
            response = login.login(request)

        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        request = self.factory.get('/logout/')
        request.session = {'info': {'id': 1, 'name': 'testuser'}}

        response = login.logout(request)

        self.assertEqual(response.status_code, 302)  # Assuming it redirects after logout
        self.assertNotIn('info', request.session)  # Assuming the session is cleared

