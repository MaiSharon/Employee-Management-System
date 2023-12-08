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


def task_list(request):

    context = {
        'page_title': 'Tasks'
    }
    return render(request, 'tasks.html', context)
