from django.shortcuts import render, redirect

from dept_app import models
from dept_app.utils.pagination import Pagination
from dept_app.utils.form import EmployeeModelForm


def get_filitered_userinfo(search):
    """返回過濾後的UserInfo數據"""
    if not search:
        return models.UserInfo.objects.all()
    else:
        search_data = {"name__contains": search}
        return models.UserInfo.objects.filter(**search_data)


def employee_list(request):

    # step1:分析搜尋條件
    search_query = request.GET.get("search", "")  # 後面""為預設空字串，讓input框內不出現None字符

    # step2:依據搜尋條件獲取數據
    filtered_userinfo = get_filitered_userinfo(search_query)

    # step3:分頁處理
    paginator = Pagination(request,filtered_userinfo, page_size=5)

    context = {
        "search": search_query,
        "queryset": paginator.page_queryset,  # 分完頁的數據
        "page_string": paginator.generate_html(),  # 頁碼
        "page_title": "Employees"

    }

    return render(request, 'employee_list.html', context)


def employee_add(request):
    if request.method == "GET":
        form = EmployeeModelForm()
        return render(request, "employee_add.html", {"form": form, "page_title": "Employee Add"})

    form = EmployeeModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/user/list/")
    return render(request, "employee_add.html", {"form": form, "page_title": "Employee Add"})


def employee_edit(request, nid):
    """編輯用戶"""
    row_object = models.UserInfo.objects.filter(id=nid).first()

    if request.method == "GET":
        # instance默認把每一個數值在欄位中顯示出來，等同於input的value值
        form = EmployeeModelForm(instance=row_object)
        return render(request, "employee_edit.html", {'form': form, "page_title": "Employee Edit"})

    # instance等於是把前面data數據指定更新到這instance這一行
    form = EmployeeModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()

        return redirect("/user/list/")
    return render(request, "employee_edit.html", {'form': form, "page_title": "Employee Edit"})


def employee_delete(request, nid):
    """刪除用戶"""
    models.UserInfo.objects.filter(id=nid).delete()

    return redirect("/user/list/")
