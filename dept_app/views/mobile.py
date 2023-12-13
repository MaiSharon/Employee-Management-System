from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_http_methods, require_GET

from dept_app import models
from dept_app.utils.form import MobileEditModelForm, MobileModelForm
from dept_app.utils.pagination import Pagination
from dept_app.utils.validate_utils import validate_search

@require_GET
def mobile_list(request):
    """
    處理展示手機設備列表的請求。支持搜尋和分頁功能。

    - GET: 返回手機設備列表，搜尋和分頁功能。

    Steps for GET:
        1. 獲取用戶的搜尋輸入。
            1.1 從 request.GET 中提取 'search' 參數值，去除頭尾空格。
        2. 使用 validate_search() 驗證搜尋輸入內容。
            2.1 若搜尋輸入不合法或空白，則展示所有手機設備數據。
            2.2 若搜尋輸入合法，則執行過濾查詢。
        3. 使用 Pagination 類對查詢結果進行分頁處理。
            3.1 計算分頁和分頁顯示的 HTML。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。

    Returns HttpResponse:
        - GET: 重渲染手機設備列表、搜尋結果、分頁和頁面標題。
    """
    # 接收用戶輸入搜尋內容
    search_input = request.GET.get('search', '').strip()  # 獲取 'search' 參數的值，若無則為空字串。去除頭尾空格
    # 驗證搜尋輸入內容
    is_valid_search_input = validate_search(search_input)
    # 搜尋或返回所有數據
    all_queryset_or_search_result = models.MobileNum.objects.filter(mobile__icontains=is_valid_search_input)
    # 分頁處理
    paginator = Pagination(request, queryset=all_queryset_or_search_result, page_size=5)

    context = {
        'search': is_valid_search_input,
        'mobiles': paginator.page_queryset,  # 分完頁的數據
        'page_string': paginator.generate_html(),  # 頁碼
        'page_title': 'Mobiles'
    }

    return render(request, 'mobile_list.html', context)

@require_http_methods(['GET', 'POST'])
def mobile_add(request):
    """
    處理新增手機設備的請求。

    - GET: 返回空白的新增手機設備表單(MobileModelForm)。
    - POST: 處理提交的手機設備數據，並添加到手機設備列表中。

    Steps for GET: 創建並顯示空的 MobileModelForm。

    Steps for POST:
        1. 驗證表單數據。
        2. 若驗證成功
            2.1. 創建並保存新 Mobile 對象。
            2.2. 重定向到手機設備列表頁面。
        3. 若驗證失敗
            3.1 顯示錯誤信息並重渲染表單。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。

    Returns HttpResponse:
        - GET: 渲染過的手機設備頁面，含空白 MobileModelForm。
        - POST:
            - 成功，重定向手機設備列表頁面。
            - 失敗，重渲染新增手機設備頁面，含錯誤信息和已填寫的 MobileModelForm。
    """
    if request.method == 'GET':
        form = MobileModelForm()
        return render(request, 'mobile_add.html', {'form': form, 'page_title': 'Mobile Add'})

    form = MobileModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('mobile_list')
    return render(request, 'mobile_add.html', {'form': form, 'page_title': 'Mobile Add'})

@require_http_methods(['GET', 'POST'])
def mobile_edit(request, nid):
    """
    處理編輯手機設備的請求。

    - GET: 返回用於編輯特定手機設備的表單(MobileEditModelForm)。
    - POST: 處理提交編輯的手機設備數據，更新特定手機設備。

    Steps for GET:
        1. 根據提供的 ID(nid)獲取特定手機設備數據。
        2. 將獲取的手機設備數據填充於 MobileEditModelForm 表單，以供展示和編輯。

    Steps for POST:
        1. 驗證編輯表單。
        2. 若驗證成功
            2.1. 更新並保存當前手機數據到特定 Mobile 對象
            2.2. 重定向手機設備列表頁面。
        3. 若驗證失敗
            3.1 顯示錯誤信息並重渲染表單。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。
        nid (int): 要編輯的手機設備 ID。

    Returns HttpResponse:
        - GET: 渲染過的編輯手機設備頁面，含已填寫的 MobileEditModelForm。
        - POST:
            - 成功，重定向手機設備列表頁面。
            - 失敗，重渲染編輯手機設備頁面，含錯誤信息和已填寫的 MobileEditModelForm。
    """
    row_object = models.MobileNum.objects.filter(id=nid).first()
    if request.method == 'GET':
        form = MobileEditModelForm(instance=row_object)
        return render(request, 'mobile_edit.html', {'form': form, 'page_title': 'Mobile Edit'})

    form = MobileEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('mobile_list')
    return render(request, 'mobile_edit.html', {'form': form, 'page_title': 'Mobile Edit'})

@require_POST
def mobile_delete(request, nid):
    """
    處理刪除手機設備的請求。

    - POST: 刪除指定的手機設備。

    Steps for POST:
        1. 根據提供的 ID(nid)獲取並刪除特定 Mobile 對象。
        2. 返回手機設備列表頁面。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。
        nid (int): 要刪除手機設備的 ID。

    Returns HttpResponse:
        - POST: 重定向手機設備列表頁面。
    """
    models.MobileNum.objects.filter(id=nid).delete()
    return redirect('mobile_list')
