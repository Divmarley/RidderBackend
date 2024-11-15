from django.urls import path
from .views import *

urlpatterns = [
    path('restaurants/', RestaurantList.as_view(), name='restaurant-list'),
    path('restaurants-create/', RestaurantListCreateView.as_view(), name='restaurant-list-create'),
    path('restaurants/<int:pk>/', RestaurantDetail.as_view(), name='restaurant-detail'),
    path('foodmenu-create/', FoodMenuCreate.as_view(), name='foodmenu-create'),
    path('foodmenu-list/', FoodMenuList.as_view(), name='foodmenu-list'),
    path('foodmenu/<int:pk>/', FoodMenuDetail.as_view(), name='foodmenu-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'), 
    # path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:id>/', OrderListByIdView.as_view(), name='order-list-by-id'),
    path('orders/<int:pk>/accept/', OrderAcceptView.as_view(), name='order-accept'),
    path('orders/<int:pk>/decline/', OrderDeclineView.as_view(), name='order-decline'),
    path('orders/<int:id>/status/', OrderStatusView.as_view(), name='order-status'),
    path('orders/', OrderListView.as_view(), name='order-list'),
]
