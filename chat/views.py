# views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer

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
