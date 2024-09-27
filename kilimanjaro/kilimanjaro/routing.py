"""Contains notification consumer routing related code"""

from django.urls import path

from notification.consumers import NotificationConsumer
from chat.consumers import ChatConsumer


websocket_urlpatterns = [
    path("notification/", NotificationConsumer.as_asgi()),
    path("chat/", ChatConsumer.as_asgi())
]
