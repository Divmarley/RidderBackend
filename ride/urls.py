from django.urls import path
from .views import PaymentListCreateView, RideHistoryListCreateView

urlpatterns = [
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('ride-history/', RideHistoryListCreateView.as_view(), name='ridehistory-list-create'),
]