"""
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings') 應該在其他所有導入之前。
確保這一行出現在您導入任何其他 Django 模塊之前。
有助於避免 AppRegistryNotReady 錯誤
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_dept.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from . import routing
from .middleware_for_asgi import CustomAuthMiddleware  # 確保這個import路徑是正確的



application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": CustomAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})
