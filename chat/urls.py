# urls.py

from django.urls import path,include
from .views import *
 

urlpatterns = [
    path('messages/', MessageListCreateAPIView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageDetailAPIView.as_view(), name='message-detail'),
    path('drivers-online/', DriverOnlineListCreateAPIView.as_view(), name='driver-online-list') ,

]
