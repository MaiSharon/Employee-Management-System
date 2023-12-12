from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from dept_app import models
from dept_app.utils.pagination import Pagination
from dept_app.utils.form import EmployeeModelForm
from dept_app.utils.validate_utils import validate_search

@require_GET
def employee_list(request):
    """
    展示員工列表並分頁、搜尋功能。

    Usage:
    - GET: 展示管理員列表、搜尋。
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

@require_http_methods(["GET", "POST"])
def employee_add(request):
    if request.method == "GET":
        form = EmployeeModelForm()
        return render(request, "employee_add.html", {"form": form, "page_title": "Employee Add"})

    form = EmployeeModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('employee_list')
    return render(request, "employee_add.html", {"form": form, "page_title": "Employee Add"})


@require_http_methods(['GET', 'POST'])
def employee_edit(request, nid):
    """編輯用戶"""
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
    """刪除用戶"""
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect('employee_list')
