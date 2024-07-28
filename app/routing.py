from django.urls import re_path

from app.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path('chat/', ChatConsumer.as_asgi())
]