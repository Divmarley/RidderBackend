from django.urls import path
from channels.routing import URLRouter

from chat.consumers import ChatConsumer
from food.consumers import FoodConsumer

websocket_urlpatterns = [
    # Add your websocket patterns here
    # Example: re_path(r'ws/some_path/$', SomeConsumer.as_asgi()),
    path('accounts/', ChatConsumer.as_asgi()),
    path('orders/', FoodConsumer.as_asgi()),
]