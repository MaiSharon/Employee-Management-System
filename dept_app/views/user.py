from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page

from dept_app import models
from dept_app.utils.pagination import Pagination
from dept_app.utils.form import UserModelForm
# from django.core import paginator
@receiver(post_save, sender=models.UserInfo)
@receiver(post_delete, sender=models.UserInfo)
def clear_cache(sender, **kwargs):
    print("hi im chche single")
    cache.delete('cache_user_list')
    updated_data = models.UserInfo.objects.all()
    cache.set('cache_user_list', updated_data, 60 * 15)

def get_filitered_userinfo(search):
    """跟玉搜索條件返回過濾後的UserInfo數據"""
    if not search:
        return models.UserInfo.objects.all()
    else:
        search_data = {"name__contains": search}
        return models.UserInfo.objects.filter(**search_data)


def user_list(request):
    # search_dict = {}
    # search = request.GET.get("search", "")  # 後面""為預設空字串，讓input框內不出現None字符
    # if search:  # 0.2.1 True 將會把獲取值新增到字典
    #     search_dict["username__contains"] = search  # 找出 username 欄位中包含特定字串的所有對象"。contains 是一種查詢類型
    #
    # queryset = models.UserInfo.objects.filter(**search_dict)



    # step1:分析搜尋條件
    search_query = request.GET.get("search", "")  # 後面""為預設空字串，讓input框內不出現None字符

    # # step2:依據搜尋條件獲取數據
    # filtered_userinfo = get_filitered_userinfo(search_query)


    # For each distinct search_query, store and retrieve its own cache
    cache_key = f'cache_user_list:{search_query}'

    # Try to get filtered userinfo from cache
    filtered_userinfo = cache.get(cache_key)
    print(filtered_userinfo)
    # If cache does not exist, query the data and set the cache
    if filtered_userinfo is None:
        filtered_userinfo = get_filitered_userinfo(search_query)
        cache.set('cache_user_list', filtered_userinfo, 60 * 15)

    # step3:分頁處理
    paginator = Pagination(request, filtered_userinfo, page_size=5)

    context = {
        "search": search_query,
        "queryset": paginator.page_queryset,  # 分完頁的數據
        "page_string": paginator.html(),  # 頁碼

    }

    return render(request, 'user_list.html', context)


# def user_form_add(request):
#     if request.method == "GET":
#         context = {
#             'gender_choices': models.UserInfo.gender_choices,
#             'depart_list': models.Department.objects.all(),
#         }
#         return render(request, 'user_form_add.html', context)
#
#     gender_id = request.POST.get('gd')
#     depart_id = request.POST.get('dp')
#
#     models.UserInfo.objects.create(gender=gender_id, depart=depart_id)
#     return redirect("/layout/")



def user_add(request):
    """"添加用戶(Model Form)版本"""
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "user_add.html", {'form': form})

    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        print("hi ,im single add")
        return redirect("/user/list/")
    return render(request, "user_add.html", {"form": form})


# TODO need fix redis
def user_edit(request, nid):
    """編輯用戶"""
    row_object = models.UserInfo.objects.filter(id=nid).first()

    if request.method == "GET":
        # instance默認把每一個數值在欄位中顯示出來，等同於input的value值
        form = UserModelForm(instance=row_object)
        return render(request, "user_edit.html", {'form': form})

    # instance等於是把前面data數據指定更新到這instance這一行
    form = UserModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        cache.delete('cache_user_list')
        return redirect("/user/list/")
    return render(request, "user_edit.html", {'form': form})


def user_delete(request, nid):
    """刪除用戶"""
    models.UserInfo.objects.filter(id=nid).delete()

    return redirect("/user/list/")
