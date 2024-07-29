from django.urls import re_path
from .consumer import VideoStreamConsumer

websocket_urlpatterns = [
    re_path('ws/stream/', VideoStreamConsumer.as_asgi()),
]
