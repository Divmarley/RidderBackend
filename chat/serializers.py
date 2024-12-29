from rest_framework import serializers
from accounts.models import CustomUser
from accounts.serializers import UserSerializer
from ride.models import TripHistory
from .models import DriverOnline, Message, Connection, RideRequest

class SearchSerializer(UserSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'name',
            'thumbnail',
            'status',
            'account_type',
            # 'distance'
        ]
    
    def get_status(self, obj):
        if hasattr(obj, 'pending_them') and obj.pending_them:
            return 'pending-them'
        elif hasattr(obj, 'pending_me') and obj.pending_me:
            return 'pending-me'
        elif hasattr(obj, 'connected') and obj.connected:
            return 'connected'
        return 'no-connection'

class RequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Connection
        fields = [
            'id',
            'sender',
            'receiver',
            'location',
            'created',
            'status',
            'extras'
            

        ]

class FriendSerializer(serializers.ModelSerializer):
    friend = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = [
            'id',
            'friend',
            'preview',
            'updated',
            'data_driver',
            'location' 
        ]

    def get_friend(self, obj):
        user = self.context['user']
        if user == obj.sender:
            return UserSerializer(obj.receiver).data
        elif user == obj.receiver:
            return UserSerializer(obj.sender).data
        else:
            raise serializers.ValidationError('No user found in FriendSerializer')

    def get_preview(self, obj):
        default = 'New connection'
        return getattr(obj, 'latest_text', default) or default

    def get_updated(self, obj):
        date = getattr(obj, 'latest_created', obj.updated) or obj.updated
        return date.isoformat()

class MessageSerializer(serializers.ModelSerializer):
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'is_me',
            'text',
            'created'
        ]

    def get_is_me(self, obj):
        return self.context['user'] == obj.user

class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = '__all__'


class TripSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Connection
        fields = [
            'id',
            'sender',
            'receiver', 
            'status',
            'paymentStatus', 
            'location',
            'data_driver'
            
        ]


# TripHistorySerializer

class TripHistorySerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = TripHistory
        fields = [
            'sender','receiver','status','paymentStatus','created_at'
        ]

  


class DriverOnlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = DriverOnline
        fields = ['driver', 'phone', 'location', 'latitude', 'longitude','is_online','push_token']