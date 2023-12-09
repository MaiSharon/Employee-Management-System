from django.shortcuts import HttpResponse, render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from dept_app import models
from dept_app.views.serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = TaskSerializer

class TaskChoicesView(APIView):
    """
    get:
    獲取任務優先級選項文字。

    返回 Task模型中任務優先級選項文字。
    """
    def get(self, request):
        return Response(models.Task.task_choices)


def task_list(request):
    """提供 layout.html網頁標題名稱"""
    return render(request, 'tasks.html', {'page_title': 'Tasks'})
