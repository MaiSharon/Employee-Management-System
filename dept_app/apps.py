from django.apps import AppConfig


class DeptAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dept_app'

    def ready(self):
        from dept_app.views.user import clear_cache