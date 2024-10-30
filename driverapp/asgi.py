# asgi.py (inside driverapp directory)

import chat.routing
import food.routing
import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driverapp.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
	'http': django_asgi_app,
	'websocket': AllowedHostsOriginValidator(
		JWTAuthMiddlewareStack(
			URLRouter(chat.routing.websocket_urlpatterns),
		)
	)
})

