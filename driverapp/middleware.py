import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware.base import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from urllib.parse import parse_qs

User = get_user_model()

class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = User.objects.get(id=payload['user_id'])
                scope['user'] = user
            except jwt.ExpiredSignatureError:
                # Handle token expiration
                scope['user'] = None
            except (jwt.DecodeError, User.DoesNotExist):
                # Handle token decoding error or user not found
                scope['user'] = None
        else:
            scope['user'] = None

        return await super().__call__(scope, receive, send)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
