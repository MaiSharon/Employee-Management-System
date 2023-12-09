import re
import logging

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


class AuthMiddleware(MiddlewareMixin):
    """登入校驗"""
    def process_request(self, request):

        # 如果沒有返回值(返回None)，繼續往後走
        # 如果有返回值 HttpResponse, render, redirect，則直接在此中間件中斷不繼續向後執行

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

        exclude_paths_regex = [re.compile(pattern) for pattern in exclude_paths]

        # 加入正則表達式以匹配動態路由
        if request.path_info.startswith('/__debug__/') or any(
                pattern.match(request.path_info) for pattern in exclude_paths_regex):
            return
        # 檢查用戶session，如果用戶未登錄且訪問的不是排除路徑，則重定向到登錄頁面
        info_dic = request.session.get('info')
        if not info_dic and not any(pattern.match(request.path_info) for pattern in exclude_paths_regex):
            logger.info(f"Non-verify user from {request.path_info} to login page")
            return redirect('/login/')
