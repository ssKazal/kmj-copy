import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from chat.middleware import TokenAuthMiddleware
from .routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kilimanjaro.settings")


application = ProtocolTypeRouter({
        "http": get_asgi_application(),
        'websocket':  AllowedHostsOriginValidator(
            TokenAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            )
        )
    })