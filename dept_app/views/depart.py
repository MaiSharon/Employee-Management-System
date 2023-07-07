from django.shortcuts import render, redirect

from dept_app import models
from dept_app.utils.pagination import Pagination


def depart_list(request):
    """部門列表"""

    # 到數據庫中獲取所有的部門列表(會是queryset的形式)
    # [對象, 對象, 對象]
    queryset = models.Department.objects.all()

    page_object = Pagination(request, queryset)
    page = page_object.page

    context = {
        "page": page,

        "queryset": page_object.page_queryset,  # 分完頁的數據條
        "page_string": page_object.html()  # 頁碼
    }
    return render(request, 'depart_list.html', context)


def depart_add(request):
    """新增部門列表"""
    if request.method == "GET":
        return render(request, 'depart_add.html')

    # 獲取
    title = request.POST.get("title")

    # 保存到數據庫
    models.Department.objects.create(title=title)

    # 重定向回部門列表
    return redirect("/depart/list/")


def depart_delete(request):
    """ 刪除部門 """
    # 獲取ID
    nid = request.GET.get('nid')
    # 刪除
    models.Department.objects.filter(id=nid).delete()

    # 跳轉回部門列表
    return redirect("/depart/list/")


# nid 是在urls.py的路徑轉換器<int:nid>中的nid
# 相當於把網址中的 http://127.0.0.1:8000/depart/1/edit/ 的1傳入
def depart_edit(request, nid):
    """修改部門"""

    # 默認頁面與內容
    if request.method == "GET":
        # 根據nid，獲取它的數據
        row_boject = models.Department.objects.filter(id=nid).first()
        return render(request, 'depart_edit.html', {'row_object': row_boject})

    # 獲取用戶提交的標題
    title = request.POST.get("title")

    # 根據id找到數據庫中的數據並進行更新
    models.Department.objects.filter(id=nid).update(title=title)

    return redirect("/depart/list/")

