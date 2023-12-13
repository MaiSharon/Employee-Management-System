from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render

from dept_app import models
from dept_app.views.serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    """
    管理 Task 實例的 API 端點。

    list:
    返回所有 Task 實例的列表。不需要任何參數。

    create:
    根據提供的數據創建一個新的 Task 實例。需要提交 Task 相關的數據。

    retrieve:
    返回指定 ID 的 Task 實例。需要 Task ID 參數。

    update:
    更新指定 ID 的 Task 實例。需要 Task ID 和更新數據。

    partial_update:
    部分更新指定 ID 的 Task 實例。需要 Task ID 和部分更新數據。

    delete:
    刪除指定 ID 的 Task 實例。需要 Task ID 參數。

    queryset: 包含所有 Task 實例的查詢集。
    serializer_class: Task 實例的序列化類。
    """
    queryset = models.Task.objects.all()
    serializer_class = TaskSerializer

class TaskChoicesView(APIView):
    """
    API 端點，用於獲取 Task 模型中定義的任務優先級選項 。

    get:
    獲取任務優先級選項文字。
    """
    def get(self, request):
        return Response(models.Task.task_choices)

def task_list(request):
    """提供 layout.html網頁標題名稱"""
    return render(request, 'tasks.html', {'page_title': 'Tasks'})
