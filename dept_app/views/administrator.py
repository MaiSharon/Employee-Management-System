import logging

from django.shortcuts import render
from django.views.decorators.http import require_GET

from dept_app import models
from dept_app.utils.pagination import Pagination
from dept_app.utils.validate_utils import validate_search

logger = logging.getLogger(__name__)

@require_GET
def admin_list(request):
    """
    處理展示管理員列表的請求。支持搜尋和分頁功能

    - GET: 返回管理員列表，搜尋和分頁功能。

    Steps for GET:
        1. 獲取用戶的搜尋輸入。
            1.1 從 request.GET 中提取 'search' 參數值，去除頭尾空格。
        2. 使用 validate_search() 驗證搜尋輸入內容。
            2.1 若搜尋輸入不合法或空白，則展示所有管理員數據。
            2.2 若搜尋輸入合法，則執行過濾查詢。
        3. 使用 Pagination 類對查詢結果進行分頁處理。
            3.1 計算分頁和分頁顯示的 HTML。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。

    Returns HttpResponse:
        - GET: 重渲染管理員列表、搜尋結果、分頁和頁面標題。
    """
    # 接收用戶輸入搜尋內容
    search_input = request.GET.get('search', '').strip()  # 獲取 'search' 參數的值，若無則為空字串。去除頭尾空格
    # 驗證搜尋輸入內容
    is_valid_search_input = validate_search(search_input)
    # 搜尋或返回所有數據
    all_queryset_or_search_result = models.Admin.objects.filter(username__icontains=is_valid_search_input)
    # 分頁處理
    page_object = Pagination(request, queryset=all_queryset_or_search_result, page_size=15)

    context = {
        'search': is_valid_search_input,
        'queryset': page_object.page_queryset,  # 分完頁的數據
        'page_string': page_object.generate_html(),  # 頁碼
        'page_title': 'Administrators'
    }

    return render(request, 'administrator.html', context)
