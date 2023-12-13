from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from dept_app import models
from dept_app.utils.pagination import Pagination
from dept_app.utils.form import EmployeeModelForm
from dept_app.utils.validate_utils import validate_search

@require_GET
def employee_list(request):
    """
    處理展示員工列表的請求。支持搜尋和分頁功能。

    - GET: 返回員工列表，搜尋和分頁功能。

    Steps for GET:
        1. 獲取用戶的搜尋輸入。
            1.1 從 request.GET 中提取 'search' 參數值，去除頭尾空格。
        2. 使用 validate_search() 驗證搜尋輸入內容。
            2.1 若搜尋輸入不合法或空白，則展示所有員工數據。
            2.2 若搜尋輸入合法，則執行過濾查詢。
        3. 使用 Pagination 類對查詢結果進行分頁處理。
            3.1 計算分頁和分頁顯示的 HTML。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。

    Returns HttpResponse:
        - GET: 重渲染員工列表、搜尋結果、分頁和頁面標題。
    """
    # 接收用戶輸入搜尋內容
    search_input = request.GET.get('search', '').strip()  # 獲取 'search' 參數的值，若無則為空字串。去除頭尾空格
    # 驗證搜尋輸入內容
    is_valid_search_input = validate_search(search_input)
    # 搜尋或返回所有數據
    all_queryset_or_search_result = models.UserInfo.objects.filter(name__icontains=is_valid_search_input)
    # 分頁處理
    paginator = Pagination(request, queryset=all_queryset_or_search_result, page_size=5)

    context = {
        'search': is_valid_search_input,
        'employees': paginator.page_queryset,  # 分完頁的數據
        'page_string': paginator.generate_html(),  # 頁碼
        'page_title': 'Employees'
    }

    return render(request, 'employee_list.html', context)

@require_http_methods(['GET', 'POST'])
def employee_add(request):
    """
    處理新增員工的請求。

    - GET: 返回用於新增員工的表單(EmployeeModelForm)。
    - POST: 處理提交新增的員工資料，並添加到員工列表中。

    Steps for GET: 創建並顯示空的 EmployeeModelForm。

    Steps for POST:
        1. 驗證表單數據。
        2. 若驗證成功
            2.1. 創建並保存新 UserInfo 對象。
            2.2. 重定向到員工列表頁面。
        3. 若驗證失敗
            3.1 顯示錯誤信息並重渲染表單。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。

    Returns HttpResponse:
        - GET: 渲染過的新增員工頁面，含空的 EmployeeModelForm。
        - POST:
            - 成功，重定向員工列表頁面。
            - 失敗，重渲染新增員工頁面，含錯誤信息和已填寫的 EmployeeModelForm。
    """
    if request.method == 'GET':
        form = EmployeeModelForm()
        return render(request, 'employee_add.html', {'form': form, 'page_title': 'Employee Add'})

    form = EmployeeModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('employee_list')
    return render(request, 'employee_add.html', {'form': form, 'page_title': 'Employee Add'})

@require_http_methods(['GET', 'POST'])
def employee_edit(request, nid):
    """
    處理編輯員工數據的請求。

    - GET: 返回用於編輯特定員工的表單(EmployeeModelForm)。
    - POST: 處理提交編輯的員工資料，更新特定員工數據。

    Steps for GET:
        1. 根據提供的 ID(nid)獲取特定員工信息。
        2. 將獲取的員工數據填充於 EmployeeModelForm 表單，以供展示和編輯。

    Steps for POST:
        1. 驗證編輯表單。
        2. 若驗證成功
            2.1. 更新並保存當前員工數據到特定 UserInfo 對象。
            2.2. 重定向到員工列表頁面。
        3. 若驗證失敗
            3.1 顯示錯誤信息並重渲染表單。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。
        nid (int): 要編輯的員工 ID。

    Returns HttpResponse:
        - GET: 渲染過的編輯員工頁面，含已填寫的 EmployeeModelForm。
        - POST:
            - 成功，重定向員工列表頁面。
            - 失敗，重渲染編輯員工頁面，含錯誤信息和已填寫的 EmployeeModelForm。
    """
    row_object = models.UserInfo.objects.filter(id=nid).first()

    if request.method == 'GET':
        # instance默認把每一個數值在欄位中顯示出來，等同於input的value值
        form = EmployeeModelForm(instance=row_object)
        return render(request, 'employee_edit.html', {'form': form, 'page_title': 'Employee Edit'})

    # instance等於是把前面data數據指定更新到這instance這一行
    form = EmployeeModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('employee_list')
    return render(request, 'employee_edit.html', {'form': form, 'page_title': 'Employee Edit'})

@require_POST
def employee_delete(request, nid):
    """
    處理刪除員工數據的請求。

    - POST: 刪除指定的員工數據。

    Steps for POST:
        1. 根據提供的 ID(nid)獲取並刪除特定 UserInfo 對象。
        2. 返回員工列表頁面。

    Args:
        request (HttpRequest): 客戶端的 HTTP 請求。
        nid (int): 要刪除員工數據的 ID。

    Returns HttpResponse:
        - POST: 重定向員工列表頁面。
    """
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect('employee_list')
