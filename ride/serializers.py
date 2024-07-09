from rest_framework import serializers
from .models import Payment, RideHistory
from accounts.models import CustomUser

class PaymentSerializer(serializers.ModelSerializer):
    payment_by = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    payment_to = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Payment
        fields = '__all__'

class RideHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RideHistory
        fields = '__all__'
