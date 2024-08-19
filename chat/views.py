# views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import DriverOnline, Message
from .serializers import DriverOnlineSerializer, MessageSerializer

class MessageListCreateAPIView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]  # Example: Requires authentication for all operations

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
        # Ensure message is saved with current authenticated user as sender

class MessageDetailAPIView(generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]



from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

class DriverOnlineListCreateAPIView(generics.ListCreateAPIView):
    # queryset = DriverOnline.objects.all()
    serializer_class = DriverOnlineSerializer
    def get_queryset(self):
        return DriverOnline.objects.filter(is_online=True)

    def create(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        location = request.data.get('location')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        is_online = request.data.get('is_online')
        push_token= request.data.get('push_token')

        # Check if a driver with the given phone number already exists
        existing_driver = DriverOnline.objects.filter(phone=phone).first()
 
        if existing_driver:
            # If exists, update the existing driver entry
            serializer = self.serializer_class(existing_driver, data=request.data, partial=True)
            if serializer.is_valid():
                # serializer.push_token.
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If does not exist, create a new driver entry
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
