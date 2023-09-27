import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from . import routing
from prj_dept.middleware_for_asgi import CustomAuthMiddleware  # 確保這個import路徑是正確的

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_dept.setting')

django_asgi_app = get_asgi_application()

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
