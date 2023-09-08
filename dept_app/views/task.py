# from django.http import JsonResponse
# from django.shortcuts import HttpResponse, render
# from django.views.decorators.csrf import csrf_exempt
# from django import forms
#
# from dept_app import models
#
# from dept_app.utils.pagination import Pagination  # 分頁組件
#
#
# class TaskModelForm(BootStrapModelForm):
#     class Meta:
#         model = models.Task
#         fields = "__all__"
#         widgets = {
#             "detail": forms.TextInput
#         }
#
#
#
# @csrf_exempt  # 他是免除CSRF Token認證
# def task_add(request):
#     """ AJAX返回值 """
#
#     form = TaskModelForm(data=request.POST)
#
#     if form.is_valid():
#         logger.info("user: %s add task title: %s, pd: %s",
#                     request.session["info"]["name"],
#                     form.cleaned_data['title'],
#                     form.cleaned_data['user']
#                     )
#         form.save()
#         dict_data = {"status": True}
#         return JsonResponse(dict_data)
#
#     dict_data = {"status": False, "error": form.errors}
#     return JsonResponse(dict_data)
#
# # def task_edit(request, nid):
# #     form = models.Task.objects.filter(id=nid).order_by("-level")
# #
# #     if request.method == "GET":
# #
# #
# #
# #     return render(request, "task_edit.html", {"form": form})
#
#
# import logging
#
# logger = logging.getLogger('views_task')
#
# def task_list(request):
#     form = TaskModelForm
#
#     # 搜尋
#     search_dict = {}
#     search = request.GET.get("search", "")
#
#     if search:
#         search_dict["mobile__contains"] = search
#
#     # 把搜尋的數據傳給分頁組件的類
#     queryset = models.Task.objects.filter(**search_dict).order_by("-level")
#
#     if not queryset:
#         print(search_dict, queryset)
#         queryset = models.Task.objects.all().order_by("-level")
#
#     page_object = Pagination(request, queryset, page_size=3)
#
#     # log
#     logger.error("task info fetched from database page: %s", page_object.page)
#
#     context = {
#         "form": form,
#         "search": search,
#         "page": page_object.page,
#         "queryset": page_object.page_queryset,  # 分完頁的數據條
#         "page_string": page_object.html()  # 頁碼
#     }
#
#     return render(request, 'task_list.html', context)
#
#
# @csrf_exempt
# def task_sayhi(request):
#     """ 給JS的返回值 """
#     print(request.POST)
#     data_dict = {"status": True, 'data': [11, 33, 44, 22]}
#     return HttpResponse(JsonResponse(data_dict))
