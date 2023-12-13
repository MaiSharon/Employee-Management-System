from unittest.mock import Mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import TestCase, RequestFactory

from dept_app.middleware.auth import AuthMiddleware

class AuthMiddlewareTest(TestCase):
    """
    用於測試 AuthMiddleware 的單元測試類。

    測試內容包括：
    - 排除特定路徑的身份驗證。
    - 對未經認證的用戶訪問進行重定向。
    - 對未經認證的API訪問返回特定狀態碼。

    Methods:
    - setUp：初始化測試環境
    - add_session_to_request：為測試請求添加 session
    - test_path_exclusion：測試排除路徑功能
    - test_unauthenticated_access：測試未認證用戶訪問的重定向
    - test_unauthenticated_api_access：測試未認證的API訪問
    """
    def setUp(self):
        """
        測試前的準備工作，包括創建模擬請求工廠和中間件實例。
        使用 Mock 函數作為 get_response 參數創建 AuthMiddleware 實例。
        """
        self.factory = RequestFactory()
        self.middleware = AuthMiddleware(get_response=Mock())

    def add_session_to_request(self, request):
        """
        為測試中的 request 對象添加空的 session。
        使用 SessionMiddleware 為請求對象 request 添加空的 session，並保存。
        """
        middleware = SessionMiddleware(lambda r: r)
        middleware.process_request(request)
        request.session.save()

    def test_path_exclusion(self):
        """
        測試 AuthMiddleware 是否正確地將特定路徑排除在身份驗證之外。

        此測試確保中間件能夠識別並正確處理在 exclude_paths 中定義的排除路徑。
        對於這些排除路徑的請求，中間件不應進行任何處理，即預期響應應為 None。

        steps:
        1. 遍歷 AuthMiddleware 中定義的排除路徑(exclude_paths)。
        2. 對於包含正則表達式的路徑模式，生成具體路徑。
        3. 對於每個排除路徑，發起 GET 請求，並確認中間件的響應為 None。
        """
        for path_pattern in AuthMiddleware.exclude_paths:
            if any(char in path_pattern for char in ['^', '$', '+', '*', '?', '|']):
                test_path = path_pattern.replace('^', '').replace('$', '').replace('.+/', 'test/')
            else:
                test_path = path_pattern

            request = self.factory.get(test_path)
            self.add_session_to_request(request)  # 添加 session
            response = self.middleware.process_request(request)
            self.assertIsNone(response, f'Path {test_path} should be excluded')

    def test_unauthenticated_access(self):
        """
        測試未認證用戶訪問非排除路徑的重定向行為。
        當未認證用戶訪問非排除路徑時，應重定向到 '/login/' 登錄頁面。
        """
        request = self.factory.get('/tasks/')
        self.add_session_to_request(request)  # 添加 session
        response = self.middleware.process_request(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Location'], '/login/')

    def test_unauthenticated_api_access(self):
        """
        測試未認證用戶訪問 API 路徑時的響應。
        當未認證用戶訪問 API 路徑時，應返回 401 狀態碼。
        """
        request = self.factory.get('/api/tasks/')
        self.add_session_to_request(request)  # 添加 session
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 401)