from django.urls import path

from food.consumers import FoodConsumer

# from .consumers import ChatConsumer
# from food.consumers import ChatConsumer

websocket_urlpatterns = [
	# path('accounts/', ChatConsumer.as_asgi()),
    path('orders/', FoodConsumer.as_asgi()),
	
]