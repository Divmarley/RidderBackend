from rest_framework import generics

from accounts.models import CustomUser
from .models import OrderItem, Restaurant, FoodMenu
from .serializers import RestaurantSerializer, FoodMenuSerializer

class RestaurantList(generics.ListCreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class RestaurantDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class FoodMenuCreate(generics.CreateAPIView):
    queryset = FoodMenu.objects.all()
    serializer_class = FoodMenuSerializer


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.exceptions import NotFound 

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(sender=self.request.user )

    def create(self, request, *arrgs, **kwargs): 
        try:
            items_data = request.data.get('items', [])
            receiver_id = request.data.get('receiver') 
            location = request.data.get('location')
            receiver = Restaurant.objects.get(id=receiver_id)
            print("receiver",receiver)
            sender =  request.user.id
            total_price = request.data.get('total_price')
            
            order_data = {
                'sender': sender,
                'receiver': receiver.id,
                'status': 'pending',
                'total_price': total_price,
                'items': items_data,
                'location':location
            }

            print("order_data", order_data)

            serializer = self.get_serializer(data=order_data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save()

            # Send message via channels
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'orders', 
                {
                    'type': 'order_message',
                    'message': f'New order created: {order.id}'
                }
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Restaurant.DoesNotExist:
            # print(serializer)
            return Response({'error': 'Receiver restaurant does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class OrderAcceptView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.receiver != request.user:
            return Response({'error': 'You can only accept orders sent to you.'}, status=status.HTTP_403_FORBIDDEN)
        instance.status = 'accepted'
        instance.save()
        return Response(self.get_serializer(instance).data)

class OrderDeclineView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.receiver != request.user:
            return Response({'error': 'You can only decline orders sent to you.'}, status=status.HTTP_403_FORBIDDEN)
        instance.status = 'declined'
        instance.save()
        return Response(self.get_serializer(instance).data)
    

class OrderStatusView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('id')
        try:
            order = Order.objects.get(id=order_id)
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            raise NotFound('Order not found')