from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ValidationError

from dept_app.utils.bootstrap import BootStrapModelForm
from dept_app import models

class DepartmentModelForm(BootStrapModelForm):
    """
    表單用於部門的新增。負責處理自定義驗證部門名稱。

    Methods：
        clean_title: 確認部門名稱規範和唯一性。
    """
    class Meta:
        model = models.Department
        fields = ['title']

    def clean_title(self):
        """
        驗證部門名稱符合規範。

        - 確認部門名稱的結尾有 '部'。
        - 確認部門名稱在系統中是唯一性。

        Returns:
            str: 驗證通過的部門名稱。

        Raises:
            ValidationError: 部門名稱不符合上述規範。
        """
        title = self.cleaned_data.get('title')
        exists = models.Department.objects.exclude(pk=self.instance.pk).filter(title=title).exists()
        if not title.endswith('部'):
            raise ValidationError('請確認是什麼部門，例: 企劃部')
        elif exists:
            raise ValidationError('部門已存在')
        return title

class DepartmentCreateView(CreateView):
    """
    處理部門創建相關的請求。

    - GET：返回空白的部門創建表單。
    - POST：處理提交的部門數據以創建新部門。

    Steps for GET:
        1. 當用戶訪問部門創建頁面時，觸發 GET 請求。
        2. 加載 'department_create.html' 模板。
        3. 通過 'form_class' 創建一個空的 DepartmentModelForm 實例。
        4. 將表單實例和額外的上下文(如: 頁面標題 'page_title')傳遞給模板。
        5. 渲染模板和表單，展示給用戶。

    Steps for POST:
        1. 用戶填寫表單並提交，觸發 POST 請求。
        2. 收集表單數據並進行驗證。
        3. 驗證成功
            3.1. 創建新的部門，也就是創建新的 model(models.Department)實例。
            3.2. 保存新創建的模型實例到數據庫
            3.3. 重定向到 success_url 指定的 URL。
        4. 驗證失敗
            4.1. 重渲染部門創建頁面，含錯誤信息和空白 DepartmentModelForm 實例。

    Attributes:
        template_name (str): 用於渲染視圖的 HTML 模板名稱
        model (Model): 此視圖中使用的 Django 數據模型
        form_class (ModelForm): 處理部門數據創建的表單類
        success_url (str): 表單提交成功後的重定向 URL
        extra_context (dict): 向模板提供附加上下文
    """
    template_name = 'department_create.html'
    model = models.Department
    form_class = DepartmentModelForm
    success_url = reverse_lazy('department_list')
    extra_context = {'page_title': 'Department Create'}

class DepartmentListView(ListView):
    """
    處理顯示部門列表的請求。使用 Django 的 ListView 來展示部門列表。

    - GET: 獲取所有部門信息並顯示在列表中。

    Steps for GET:
        1. 使用指定的 model(models.Department)從數據庫中獲取部門數據。
        2. 將獲取的部門數據列表儲存在 context_object_name('departments')指定的變量中。
        3. 使用 template_name('department_list.html')指定的模板渲染頁面。
        4. 將額外的上下文(如: 頁面標題 'page_title')傳遞給模板。

    Attributes:
        template_name (str): 用於渲染視圖的 HTML 模板名稱
        model (Model): 此視圖中使用的 Django 數據模型
        context_object_name (str): 在模板中用於部門列表的變量名
        extra_context (dict): 向模板提供附加上下文
    """
    template_name = 'department_list.html'
    model = models.Department
    context_object_name = 'departments'
    extra_context = {'page_title': 'Departments List'}

class DepartmentUpdateView(UpdateView):
    """
    處理更新部門信息的請求。使用 Django 的 UpdateView 來更新指定部門的信息。

    - GET: 顯示特定部門的編輯表單。
    - POST: 處理提交的部門數據以更新部門信息。

    Steps for GET:
        1. 從 URL 參數中獲取部門的唯一標識（'nid'）。
        2. 使用 'get_object' 方法根據 'nid' 從 'models.Department' 中獲取相應的部門實例。
        3. 使用 'form_class' 創建帶有部門實例數據的表單。
        4. 使用 'template_name' 指定的模板渲染頁面，並將表單實例傳遞給模板。
        5. 將額外的上下文（如 'page_title'）傳遞給模板。

    Steps for POST:
        1. 接收用戶提交的表單數據。
        2. 使用 'form_class' 進行數據驗證。
        3. 驗證成功
            3.1. 更新部門信息。
            3.2. 重定向到 'success_url' 指定的 URL。
        4. 驗證失敗
            4.1. 重新渲染編輯頁面，含錯誤信息和已填充的表單。

    Attributes:
        template_name (str): 用於渲染視圖的 HTML 模板名稱。
        model (Model): 此視圖中使用的 Django 數據模型。
        form_class (ModelForm): 處理部門數據更新的表單類。
        success_url (str): 表單提交成功後的重定向 URL。
        extra_context (dict): 向模板提供附加上下文，例如: 頁面標題 'page_title'。

    Methods:
        get_object: 重寫此方法以根據 URL 中的 'nid' 參數獲取部門實例。
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
    處理刪除部門的請求。使用 Django 的 DeleteView 來實現部門的刪除功能。

    由於 DeleteView 預設是使用 GET 請求來顯示刪除確認頁面，但在這個實現中，GET 請求
    直接處理了刪除操作並重定向，沒有刪除確認過程。

    - GET: 直接刪除特定部門，然後重定向。
    - POST: 處理刪除特定部門的請求。

    Steps for GET and POST:
        1. 從 URL 參數中獲取部門的唯一標識（'nid'）。
        2. 使用 'get_object' 方法根據 'nid' 從 'models.Department' 中獲取相應的部門實例。
        3. 調用 'delete' 方法刪除該部門實例。
        4. 重定向到 'success_url' 指定的 URL。

    Attributes:
        success_url (str): 表單提交成功後的重定向 URL。

    Methods:
        get_object: 重寫此方法以根據 URL 中的 'nid' 參數獲取部門實例。
        get: 重寫此方法使 GET 請求直接執行刪除操作。
        post: 重寫此方法以處理 POST 請求的刪除操作。
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
