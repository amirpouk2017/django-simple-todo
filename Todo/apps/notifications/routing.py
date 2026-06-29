from django.urls import path
from .consumers import HelloConsumer

websocket_urlpatterns = [
    path("ws/hello/", HelloConsumer.as_asgi()),
]
