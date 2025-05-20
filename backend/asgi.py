import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import device.routing  # Import from your app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Replace with your project name

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            device.routing.websocket_urlpatterns
        )
    ),
})


app = application 