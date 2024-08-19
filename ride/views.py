 
from rest_framework import generics

from chat.serializers import TripHistorySerializer
from .models import Payment, RideHistory, TripHistory
from .serializers import PaymentSerializer, RideHistorySerializer

class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self): 
        return Payment.objects.filter(payment_by=self.request.user.id)


    # payment_by

class RideHistoryListCreateView(generics.ListCreateAPIView):
    # queryset = RideHistory.objects.all()
    serializer_class = RideHistorySerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return RideHistory.objects.filter(user=self.request.user.id)


class TripHistoryListView(generics.ListCreateAPIView):
    # queryset = RideHistory.objects.all()
    serializer_class =  TripHistorySerializer

    def get_queryset(self):
        
        print("self.request.user.id",self.request.user)
        if (self.request.user.account_type == 'driver'):
            return  TripHistory.objects.filter(driver_id=self.request.user.id)
        else:
            id = self.kwargs.get('rider_id') 
            return  TripHistory.objects.filter(rider_id=self.request.user.id)



""" 
    {
        "destination": "New York",
        "trip_time": "2024-07-01T10:00:00Z",
        "price": "50.00",
        "payment_method": "Credit Card",
        "date": "2024-07-01",
        "payment_by": 1,
        "payment_to": 2
    } 
"""