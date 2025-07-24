import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# Set settings before importing Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driverapp.settings')
django.setup()  # explicitly setup Django (optional but useful here)

# Initialize Django ASGI app early
django_asgi_app = get_asgi_application()

# ✅ Now import this AFTER Django is ready
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack

# Import routing after apps are loaded
import chat.routing
import food.routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns +
                food.routing.websocket_urlpatterns
            )
        )
    ),
})
