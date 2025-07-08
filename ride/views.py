 
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
            print('driver')
            return  TripHistory.objects.filter(driver=self.request.user.id).order_by('-created_at')
        else:
            id = self.kwargs.get('rider') 
            print('rider',)
            return  TripHistory.objects.filter(rider=self.request.user.id).order_by('-created_at')



 