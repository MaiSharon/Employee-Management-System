"""
ASGI config for prj_dept project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from . import routing



from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_dept.setting')

django_asgi_app = get_asgi_application()

# support HTTP and WebSocket

application = ProtocolTypeRouter({
    "http": django_asgi_app,  # automatic find urls.py and find views function ==> HTTP
    "websocket": AuthMiddlewareStack(  # routings(urls)、 consumers(views)
        AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
    ),
}
)