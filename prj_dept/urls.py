from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from dept_app.views import depart, pretty, user, admin, account, task, register
from django.views.generic import TemplateView

urlpatterns = [

    path('about/', TemplateView.as_view(template_name="no_js.html")),
    # path('admin/', admin.site.urls),
    path('depart/list/', depart.depart_list),
    path('depart/add/', depart.depart_add),
    path('depart/delete/', depart.depart_delete),
    path('depart/<int:nid>/edit/', depart.depart_edit),

    path('user/list/', user.user_list),
    path('user/add/', user.user_add),
    path('user/<int:nid>/edit/', user.user_edit),
    path('user/<int:nid>/delete/', user.user_delete),

    path('pretty/list/', pretty.pretty_list),
    path('pretty/add/', pretty.pretty_add),
    path('pretty/<int:nid>/edit/', pretty.pretty_edit),
    path('pretty/<int:nid>/delete/', pretty.pretty_delete),

    path('admin/list/', admin.admin_list, name="admin_list"),
    path('admin/add/', admin.admin_add, name="admin_add"),
    path('admin/<int:nid>/edit/', admin.admin_edit, name="admin_edit"),
    path('admin/<int:nid>/delete/', admin.admin_delete, name="admin_delete"),
    path('admin/<int:nid>/reset/', admin.admin_reset, name="admin_reset"),

    # path('image/add/', image.image_add),
    # path('image/<int:nid>/delete/', image.image_delete),

    path('login/', account.login, name="login"),
    path('register/', register.register_popup, name="index"),
    path('logout/', account.logout),
    path('image/code/', account.image_code),

    path('task/', task.task_list),
    path('task/ajax/', task.task_sayhi),
    path('task/add/', task.task_add),
    # path('task/<int:nid>/edit/', task.task_edit),

]

# 意思是說在生產環境下這個URL是無法訪問的
if settings.DEBUG:
    urlpatterns += [
                       path('__debug__/', include('debug_toolbar.urls')),
                   ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

