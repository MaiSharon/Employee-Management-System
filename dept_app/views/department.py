from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ValidationError

from dept_app.utils.bootstrap import BootStrapModelForm
from dept_app import models

class DepartmentModelForm(BootStrapModelForm):
    """
    處理部門的表單驗證。

    Usage:
    - 用於 Django 的 CreateView 或 UpdateView。

    Main Features：
    - 驗證 'title' 欄位以確保其以 '部' 結尾。
    - 檢查部門名稱是否已存在。

    Methods：
        clean_title: 驗證 'title' 欄位並處理可能的錯誤。
    """
    class Meta:
        model = models.Department
        fields = ['title']
    def clean_title(self):
        title = self.cleaned_data.get('title')
        exists = models.Department.objects.exclude(pk=self.instance.pk).filter(title=title).exists()
        if not title.endswith('部'):
            raise ValidationError('請確認是什麼部門，例: 企劃部')
        elif exists:
            raise ValidationError('部門已存在')
        return title


class DepartmentCreateView(CreateView):
    """
    創建部門實例。

    Usage:
    - HTTP GET：顯示空白的部門創建表單。
    - HTTP POST：驗證表單並創建新的部門實例。

    Main Features：
    - 顯示部門創建表單。
    - 驗證並保存表單數據。

    Attributes:
    template_name (str): 模板名稱。
    model (Model): 使用的數據模型。
    form_class (ModelForm): 使用的表單類。
    success_url (str): 成功後的重定向 URL。
    extra_context (dict): 額外的模板上下文。
    """
    template_name = 'department_create.html'
    model = models.Department
    form_class = DepartmentModelForm
    success_url = reverse_lazy('department_list')
    extra_context = {'page_title': 'Department Create'}


class DepartmentListView(ListView):
    """
    展示部門實例的列表。

    Usage:
    - HTTP GET：顯示所有部門的列表。

    Main Features：
    - 提取所有部門實例。
    - 以列表形式顯示。

    Attributes:
    template_name (str): 模板名稱。
    model (Model): 使用的數據模型。
    context_object_name (str): 上下文對象名稱。
    extra_context (dict): 額外的模板上下文。
    """
    template_name = 'department_list.html'
    model = models.Department
    context_object_name = 'departments'
    extra_context = {'page_title': 'Departments List'}


class DepartmentUpdateView(UpdateView):
    """
    更新部門實例。

    Usage:
    - HTTP GET：顯示帶有當前數據的部門更新表單。
    - HTTP POST：驗證表單並更新部門實例。

    Main Features：
    - 顯示部門更新表單。
    - 驗證並保存表單數據。

    Attributes:
    template_name (str): 模板名稱。
    model (Model): 使用的數據模型。
    form_class (ModelForm): 使用的表單類。
    success_url (str): 成功後的重定向 URL。
    extra_context (dict): 額外的模板上下文。
    """
    template_name = 'department_edit.html'
    model = models.Department
    form_class = DepartmentModelForm
    success_url = reverse_lazy('department_list')
    extra_context = {'page_title': 'Department Edit'}

    def get_object(self, queryset=None):
        nid = self.kwargs.get('nid')
        return models.Department.objects.get(id=nid)


class DepartmentDeleteView(DeleteView):
    """
    刪除部門實例。

    Usage：
    - HTTP GET：內部觸發 HTTP POST 方法以處理刪除。
    - HTTP POST：刪除由 nid 提供的 id 部門實例。

    Main Features：
    - 從 URL 中取得 'nid'，找到該數據實例。
    - 刪除部門實例。
    - 成功刪除後重定向到 'department_list' 頁面。

    Methods：
        get_object(queryset=None): 使用 URL 中的 'nid' 獲取部門實例。
        get(request, *args, **kwargs): 內部觸發 post() 方法以刪除部門實例。
        post(request, *args, **kwargs): 刪除部門實例，並重定向到 'department_list' 頁面。

    Steps：
    1. 從 URL 中獲取 'nid' 參數。
        1.1 如果找不到 'nid'，則引發 404 錯誤。
    2. 使用 'nid' 獲取部門實例。
    3. 刪除部門實例。
    4. 重定向到 'department_list' 頁面。
    """
    success_url = reverse_lazy('department_list')

    def get_object(self, queryset=None):
        nid = self.kwargs.get('nid')
        return models.Department.objects.get(id=nid)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

