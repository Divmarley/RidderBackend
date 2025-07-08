import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack

# Set DJANGO_SETTINGS_MODULE before anything Django-dependent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driverapp.settings')

# Initialize Django before importing any models/routing that uses them
django_asgi_app = get_asgi_application()

# Now it's safe to import routing that touches models or apps
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
    )
})

