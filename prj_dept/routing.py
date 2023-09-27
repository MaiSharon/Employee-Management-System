from django.urls import path
from dept_app import consumers

websocket_urlpatterns = [
    path("ws/chat/<str:room_name>/", consumers.ChatConsumer.as_asgi()),
]
