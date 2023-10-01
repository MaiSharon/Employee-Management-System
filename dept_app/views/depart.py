from django.shortcuts import render, redirect

from dept_app import models


def depart_list(request):
    """
    展示部門列表
    """

    queryset = models.Department.objects.all()

    context = {
        "queryset": queryset,
        "page_title": "Departments"
    }

    return render(request, 'depart_list.html', context)


def depart_add(request):
    """
    新增部門列表。

    Args:
        request (HttpRequest): Django的HTTP請求對象。

    Returns:
        HttpResponse: 基於請求類型，返回相應的HTML頁面或重定向。

    Steps:
        1. 檢查請求類型（GET或POST）。
            1.1 如果是GET請求，返回空的新增部門表單。
            1.2 如果是POST請求，添加新部門。
    """
    if request.method == "GET":
        return render(request, 'depart_add.html',{"page_title": "Department Add"})

    # 獲取
    title = request.POST.get("title")

    # 保存到數據庫
    models.Department.objects.create(title=title)

    # 重定向回部門列表
    return redirect("/depart/list/")


def depart_delete(request, nid):
    """ 刪除部門 """

    # 刪除
    models.Department.objects.filter(id=nid).delete()

    # 跳轉回部門列表
    return redirect("/depart/list/")


def depart_edit(request, nid):
    """修改部門"""

    # 默認頁面與內容
    if request.method == "GET":
        # 根據nid，獲取它的數據
        row_object = models.Department.objects.filter(id=nid).first()
        return render(request, 'depart_edit.html', {'row_object': row_object,"page_title": "Department Edit"})

    # 獲取用戶提交的標題
    title = request.POST.get("title")

    # 根據id找到數據庫中的數據並進行更新
    models.Department.objects.filter(id=nid).update(title=title)

    return redirect("/depart/list/")

