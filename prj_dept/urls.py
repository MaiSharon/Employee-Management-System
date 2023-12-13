from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers
from rest_framework import permissions

from dept_app.views import department, mobile, employee, administrator, login, tasks, register

# def trigger_error(request):
#   division_by_zero = 1 / 0

  # urlpatterns = [
  #   path('sentry-debug/', trigger_error),
  #   # ...
  # ]

schema_view = get_schema_view(
   openapi.Info(
      title="Task Management API",
      default_version='v1',
      description="提供任務的 CRUD 操作的 RESTful API 服務。",
      terms_of_service="https://quacqksort.be",
      contact=openapi.Contact(email="ppp300a@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'tasks', tasks.TaskViewSet)

urlpatterns = [
    # 公共路徑
    path('login/', login.login, name='login'),
    path('logout/', login.logout, name='logout'),
    path('register/', register.register, name='register'),
    path('verify/<str:token>/', register.verify_email, name='verify_email'),
    path('re-verify/', register.re_verify, name='re_verify'),
    path('image/code/', login.image_code, name='image_code'),

    # 任務管理
    path('tasks/', tasks.task_list, name='tasks'),
    path('api/task-choices/', tasks.TaskChoicesView.as_view(), name='task-choices'),

    # 部門管理
    path('departments/', department.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', department.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:nid>/edit/', department.DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/<int:nid>/delete/', department.DepartmentDeleteView.as_view(), name='department_delete'),

    # 員工管理
    path('employees/', employee.employee_list, name='employee_list'),
    path('employees/create/', employee.employee_add, name='employee_create'),
    path('employees/<int:nid>/edit/', employee.employee_edit, name='employee_edit'),
    path('employees/<int:nid>/delete/', employee.employee_delete, name='employee_delete'),

    # 移動設備管理
    path('mobiles/', mobile.mobile_list, name='mobile_list'),
    path('mobiles/create/', mobile.mobile_add, name='mobile_create'),
    path('mobiles/<int:nid>/edit/', mobile.mobile_edit, name='mobile_edit'),
    path('mobiles/<int:nid>/delete/', mobile.mobile_delete, name='mobile_delete'),

    # 管理員
    path('administrators/', administrator.admin_list, name='admin_list'),

    # API 路徑
    path('api/', include(router.urls)),

    # 錯誤觸發工具
    # path('sentry-debug/', trigger_error),
]

# 調試工具路徑
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
        path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


