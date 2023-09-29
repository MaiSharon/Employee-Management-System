from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView

from dept_app.views import depart, mobile, user, admin, login, task, register,chat


def trigger_error(request):
  division_by_zero = 1 / 0

  # urlpatterns = [
  #   path('sentry-debug/', trigger_error),
  #   # ...
  # ]
urlpatterns = [
    path('about/', TemplateView.as_view(template_name="no_js.html")),

    # asgi test
    path("chat/", chat.index, name="index"),
    path("chat/<str:room_name>/", chat.room, name="room"),

    # path('sentry-debug/', trigger_error),
    # path('admin/', admin.site.urls),
    path('depart/list/', depart.depart_list, name='depart_list'),
    path('depart/add/', depart.depart_add, name='depart_add'),
    path('depart/<int:nid>/edit/', depart.depart_edit, name='depart_edit'),
    path('depart/<int:nid>/delete/', depart.depart_delete, name='depart_delete'),

    path('user/list/', user.user_list, name='user_list'),
    path('user/add/', user.user_add, name='user_add'),
    path('user/<int:nid>/edit/', user.user_edit, name='user_edit'),
    path('user/<int:nid>/delete/', user.user_delete, name='user_delete'),

    path('mobile/list/', mobile.mobile_list, name='mobile_list'),
    path('mobile/add/', mobile.mobile_add, name='mobile_add'),
    path('mobile/<int:nid>/edit/', mobile.mobile_edit, name='mobile_edit'),
    path('mobile/<int:nid>/delete/', mobile.mobile_delete, name='mobile_delete'),

    path('admin/list/', admin.admin_list, name="admin_list"),
    path('admin/<int:nid>/edit/', admin.admin_edit, name="admin_edit"),
    path('admin/<int:nid>/reset/', admin.admin_reset, name="admin_reset"),

    path('register/', register.register, name="register"),
    path('verify/<str:token>/', register.verify_email, name='verify_email'),
    path('re-verify/', register.re_verify, name='re_verify'),

    path('login/', login.login, name="login"),
    path('logout/', login.logout, name="logout"),
    path('image/code/', login.image_code, name="image_code"),

    path('task/', task.task_list),
    path('task/ajax/', task.task_sayhi),
    path('task/add/', task.task_add),
    # path('task/<int:nid>/edit/', task.task_edit),

]

# 在生產環境下這個URL是無法訪問的
if settings.DEBUG:
    urlpatterns += [
                       path('__debug__/', include('debug_toolbar.urls')),
                   ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

