from django.urls import path
from .views import *

urlpatterns = [
    path('restaurants/', RestaurantList.as_view(), name='restaurant-list'),
    path('restaurants-create/', RestaurantListCreateView.as_view(), name='restaurant-list-create'),
    path('restaurants/<int:pk>/', RestaurantDetail.as_view(), name='restaurant-detail'),
    path('foodmenu/', FoodMenuCreate.as_view(), name='foodmenu-create'),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:id>/', OrderListByIdView.as_view(), name='order-list-by-id'),
    path('orders/<int:pk>/accept/', OrderAcceptView.as_view(), name='order-accept'),
    path('orders/<int:pk>/decline/', OrderDeclineView.as_view(), name='order-decline'),
    path('orders/<int:id>/status/', OrderStatusView.as_view(), name='order-status'),
]
