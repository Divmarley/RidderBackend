import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack

# Set the Django settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driverapp.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django.setup()

# Import your routing configuration
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

