from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers
from rest_framework import permissions

from dept_app.views import department, mobile, employee, administrator, login, tasks, register

def trigger_error(request):
  division_by_zero = 1 / 0

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
    path('api/', include(router.urls)),

    path('sentry-debug/', trigger_error),
    path('departments/', department.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', department.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:nid>/edit/', department.DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/<int:nid>/delete/', department.DepartmentDeleteView.as_view(), name='department_delete'),

    path('employees/', employee.employee_list, name='employee_list'),
    path('employees/create/', employee.employee_add, name='employee_create'),
    path('employees/<int:nid>/edit/', employee.employee_edit, name='employee_edit'),
    path('employees/<int:nid>/delete/', employee.employee_delete, name='employee_delete'),

    path('mobiles/', mobile.mobile_list, name='mobile_list'),
    path('mobiles/create/', mobile.mobile_add, name='mobile_create'),
    path('mobiles/<int:nid>/edit/', mobile.mobile_edit, name='mobile_edit'),
    path('mobiles/<int:nid>/delete/', mobile.mobile_delete, name='mobile_delete'),

    path('administrators/', administrator.admin_list, name='admin_list'),

    path('register/', register.register, name='register'),
    path('verify/<str:token>/', register.verify_email, name='verify_email'),
    path('re-verify/', register.re_verify, name='re_verify'),

    path('login/', login.login, name='login'),
    path('logout/', login.logout, name='logout'),
    path('image/code/', login.image_code, name='image_code'),

    path('tasks/', tasks.task_list, name='tasks'),
    path('api/task-choices/', tasks.TaskChoicesView.as_view(), name='task-choices'),

]

# 在生產環境下這個URL是無法訪問的
if settings.DEBUG:
    urlpatterns += [
                    path('__debug__/', include('debug_toolbar.urls')),
                    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
                    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
                   ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

