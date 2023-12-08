from django.http import JsonResponse
from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt
from django import forms

from dept_app.utils.bootstrap import BootStrapModelForm

from dept_app.utils.pagination import Pagination  # 分頁組件
from dept_app.utils.validate_utils import validate_search

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from dept_app import models
from dept_app.views.serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = TaskSerializer

class TaskChoicesView(APIView):
    def get(self, request):
        return Response(models.Task.task_choices)

import logging

logger = logging.getLogger('views_task')

def task_list(request):
    # form = TaskModelForm
    # 接收用戶輸入搜尋內容
    search_input = request.GET.get('search', '').strip()  # 獲取 'search' 參數的值，若無則為空字串。去除頭尾空格
    # 驗證搜尋輸入內容
    is_valid_search_input = validate_search(search_input)

    # 搜尋或返回所有數據
    all_queryset_or_search_result = models.Task.objects.filter(title__icontains=is_valid_search_input)

    # 分頁處理
    paginator = Pagination(request, queryset=all_queryset_or_search_result, page_size=3)

    # log
    logger.error("task info fetched from database page: %s", paginator.page)

    context = {
        # 'form': form,
        'search': is_valid_search_input,
        'tasks': paginator.page_queryset,  # 分完頁的數據
        'page_string': paginator.generate_html(),  # 頁碼
        'page_title': 'Tasks'

    }
    return render(request, 'tasks.html', context)


# class TaskModelForm(BootStrapModelForm):
#     class Meta:
#         model = models.Task
#         fields = "__all__"
#         widgets = {
#             "detail": forms.TextInput
#         }



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

# def task_edit(request, nid):
#     form = models.Task.objects.filter(id=nid).order_by("-level")
#
#     if request.method == "GET":
#
#
#
#     return render(request, "task_edit.html", {"form": form})





# @csrf_exempt
# def task_sayhi(request):
#     """ 給JS的返回值 """
#     print(request.POST)
#     data_dict = {"status": True, 'data': [11, 33, 44, 22]}
#     return HttpResponse(JsonResponse(data_dict))
