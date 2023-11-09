from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods, require_GET

from dept_app import models
from dept_app.utils.form import MobileEditModelForm, MobileModelForm
from dept_app.utils.pagination import Pagination
from dept_app.utils.validate_utils import validate_search

@require_GET
def mobile_list(request):
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

    return render(request, "mobile_list.html", context)

@require_http_methods(["GET", "POST"])
def mobile_add(request):
    if request.method == "GET":
        form = MobileModelForm()
        return render(request, "mobile_add.html", {"form": form, "page_title": "Mobile Add"})

    form = MobileModelForm(data=request.POST)
    if form.is_valid():
        # 如果校驗成功，保存到數據庫
        form.save()
        return redirect("/mobile/list/")
    return render(request, "mobile_add.html", {"form": form, "page_title": "Mobile Add"})


@require_http_methods(['GET', 'POST'])
def mobile_edit(request, nid):

    row_object = models.MobileNum.objects.filter(id=nid).first()
    if request.method == "GET":
        form = MobileEditModelForm(instance=row_object)
        return render(request, "mobile_edit.html", {"form": form, "page_title": "Mobile Edit"})

    form = MobileEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 如果校驗成功，保存到數據庫
        form.save()
        return redirect('mobile_list')
    return render(request, "mobile_edit.html", {"form": form, "page_title": "Mobile Edit"})

@require_POST
def mobile_delete(request, nid):
    models.MobileNum.objects.filter(id=nid).delete()
    return redirect('mobile_list')

