import re
import logging

from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class AuthMiddleware(MiddlewareMixin):
    """
    用戶登入驗證中間件，負責處理用戶登入狀態和訪問控制。

    Attributes:
        exclude_paths (list[str]): 不需要登入即可訪問的 URL 列表

    Methods:
        process_request: 處理 HTTP 請求以驗證用戶登入狀態和管理可訪問的路徑
    """
    exclude_paths = [
        '/swagger/',
        '/sentry-debug/',
        '/re-verify/',
        '/login/',
        '/register/',
        '/image/code/',
        r'^/verify/.+/$',
        '/api/task-choices/'
    ]

    def __init__(self, get_response=None):
        """
        初始化 AuthMiddleware。

        在這裡，get_response 是一個回調函數，用於將控制權傳遞給 Django 中間件中的下一個中間件或最終的視圖函數。
        當一個中間件完成其處理並準備將請求傳遞到下一個環節時，會調用 get_response 函數。

        Args:
            get_response (callable): Django 中間件架構中用於執行下一個中間件或視圖的回調函數。
        """
        super().__init__(get_response)
        # 編譯排除路徑的正則表達式
        self.exclude_paths_regex = [re.compile(pattern) for pattern in self.exclude_paths]

    def process_request(self, request):
        """
        處理進入的 HTTP 請求。負責驗證用戶登入狀態、管理可訪問的路徑。

        Steps:
        1. 檢查當前訪問路徑是否在排除路徑列表中。
        2. 若在排除路徑列表中，允許請求繼續。
        3. 若不在排除路徑列表中，則檢查用戶的 session 是否包含登入信息。
        4. 若用戶 session 中無登入信息，則重定向到登入頁面。

        Args:
            request (HttpRequest): 客戶端的 HTTP 請求。

        Returns:
            HttpResponse or None: 若用戶未登入且訪問非排除路徑，則重定向到登入頁面。否則，返回 None 以繼續處理請求。
        """
        # 檢查訪問路徑是否在排除路徑中
        if request.path_info.startswith('/__debug__/') or any(
                pattern.match(request.path_info) for pattern in self.exclude_paths_regex):
            return

        # 檢查用戶的 session 是否包含登入信息
        info_dic = request.session.get('info')
        if not info_dic:
            # 對於API請求返回401，對於普通請求重定向到登入頁
            if request.path_info.startswith('/api/'):
                return HttpResponse(status=401)
            else:
                logger.info(f"Non-verify user from {request.path_info} to login page")
                return redirect('/login/')
