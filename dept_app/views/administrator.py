from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods

from dept_app import models
from dept_app.utils.pagination import Pagination
from dept_app.utils.validate_utils import validate_search

import logging

logger = logging.getLogger(__name__)

@require_GET
def admin_list(request):
    """
    展示管理員列表並分頁、搜尋功能。

    Usage:
    - GET: 展示管理員列表、搜尋。
    """
    # 接收用戶輸入搜尋內容
    search_input = request.GET.get("search", "").strip()  # 獲取 'search' 參數的值，若無則為空字串。去除頭尾空格
    # 驗證搜尋輸入內容
    is_valid_search_input = validate_search(search_input)

    # 搜尋或返回所有數據
    all_queryset_or_search_result = models.Admin.objects.filter(username__icontains=is_valid_search_input)

    # 分頁處理
    page_object = Pagination(request, queryset=all_queryset_or_search_result, page_size=15)

    context = {
        "search": is_valid_search_input,
        "queryset": page_object.page_queryset,  # 分完頁的數據
        "page_string": page_object.generate_html(),  # 頁碼
        "page_title": "Administrators"
    }

    return render(request, "administrator.html", context)
