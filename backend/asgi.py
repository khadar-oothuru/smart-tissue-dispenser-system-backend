# backend/asgi.py
import os
from django.core.asgi import get_asgi_application

# Set Django settings module FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Initialize Django ASGI application BEFORE importing anything else
django_asgi_app = get_asgi_application()

# NOW import channels and your routing after Django is initialized
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import device.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Use the pre-initialized Django app
    "websocket": AuthMiddlewareStack(
        URLRouter(
            device.routing.websocket_urlpatterns
        )
    ),
})

app = application