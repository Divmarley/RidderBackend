from django.urls import path
from .views import *

urlpatterns = [
    path('restaurants/', RestaurantAPIView.as_view(), name='restaurant-list-create'),
    path('restaurants-create/', create_restaurant, name='restaurant-create'),
    # path('restaurants/<int:pk>/', get_restaurant_by_id, name='get_restaurant_by_id'),
    path('restaurants-list/', RestaurantListView.as_view(), name='restaurant-list'),
    # path('restaurants-create/', RestaurantListCreateView.as_view(), name='restaurant-list-create'),
    path('restaurants/<int:pk>/', RestaurantDetail.as_view(), name='restaurant-detail'),
    path('foodmenu-create/', FoodMenuCreate.as_view(), name='foodmenu-create'),
    path('foodmenu-list/', FoodMenuList.as_view(), name='foodmenu-list'),
    path('foodmenu-list-user-restaurants/<int:pk>/', UserFoodMenuList.as_view(), name='foodmenu-list-user-restaurants'),
    path('foodmenu/<int:pk>/', FoodMenuDetail.as_view(), name='foodmenu-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'), 
    # path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:id>/', OrderListByIdView.as_view(), name='order-list-by-id'),
    path('orders/<int:pk>/accept/', OrderAcceptView.as_view(), name='order-accept'),
    path('orders/<int:pk>/decline/', OrderDeclineView.as_view(), name='order-decline'),
    path('orders/<int:id>/status/', OrderStatusView.as_view(), name='order-status'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('order-foodmenu-count/', OrderAndFoodMenuCountView.as_view(), name='order-foodmenu-count'),
    path('reviews/create/<int:food_menu_id>/', ReviewCreateView.as_view(), name='create-review'),
    path('reviews/count/<int:food_menu_id>/', ReviewCountView.as_view(), name='review-count'),
]
