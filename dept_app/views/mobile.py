from django.shortcuts import render, redirect

from dept_app import models
from dept_app.utils.form import MobileEditModelForm, MobileModelForm


def mobile_list(request):

    search_dict = {}
    search = request.GET.get("search", "")  # 預設為空字串，讓input不出現None保持乾淨空的

    #
    if search:
        search_dict["Mobiles__contains"] = search  # 字典鍵值的值的新增方式

    # 分頁組件化
    from dept_app.utils.pagination import Pagination

    # 把調數據傳給分頁組件的類
    queryset = models.MobileNum.objects.filter(**search_dict).order_by("-brand")

    if not queryset:
        print(search_dict, queryset)
        queryset = models.MobileNum.objects.all().order_by("-brand")

    page_object = Pagination(request, queryset)

    page = page_object.page


    context = {
        "search": search,
        "page": page,

        "queryset": page_object.page_queryset,  # 分完頁的數據條
        "page_string": page_object.html(), # 頁碼
        "page_title": "Mobiles"
    }

    return render(request, "mobile_list.html", context)


def mobile_add(request):
    if request.method == "GET":
        form = MobileModelForm()
        return render(request, "mobile_add.html", {"form": form, "page_title": "Mobiles Add"})

    form = MobileModelForm(data=request.POST)
    if form.is_valid():
        # 如果校驗成功，保存到數據庫
        form.save()
        return redirect("/mobile/list/")
    return render(request, "mobile_add.html", {"form": form, "page_title": "Mobiles Add"})



def mobile_edit(request, nid):

    row_object = models.MobileNum.objects.filter(id=nid).first()
    if request.method == "GET":
        form = MobileEditModelForm(instance=row_object)
        return render(request, "mobile_edit.html", {"form": form, "page_title": "Mobiles Edit"})

    form = MobileEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 如果校驗成功，保存到數據庫
        form.save()
        return redirect("/mobile/list/")
    return render(request, "mobile_edit.html", {"form": form, "page_title": "Mobiles Edit"})


def mobile_delete(request, nid):
    models.MobileNum.objects.filter(id=nid).delete()
    return redirect("/mobile/list/")
