"""
ASGI config for prj_dept project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""
from channels.routing import ProtocolTypeRouter, URLRouter
from . import routing

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_dept.settings')

# application = get_asgi_application()

# support HTTP and WebSocket
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(routing.wesocket_urlpatterns),
})


