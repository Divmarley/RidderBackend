from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
 
class Connection(models.Model):
    sender = models.OneToOneField(
        CustomUser,
        related_name='sent_connections',
        on_delete=models.CASCADE,
        # unique=True
    )
    location = models.JSONField()
    status = models.CharField(max_length=300)
    paymentStatus=models.CharField(max_length=200)
    receiver = models.ForeignKey(
        CustomUser,
        related_name='received_connections',
        on_delete=models.CASCADE
    )
    extras = models.JSONField(null=True,blank=True)
    pushToken= models.CharField(max_length=2000)
    riderPushToken= models.CharField(max_length=2000)
    accepted = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    data_driver =models.JSONField(null=True,blank=True)

    def __str__(self):
        return f'{self.sender.phone} -> {self.receiver.phone}'
    
# class FoodConnection(models.Model):
#     sender = models.ForeignKey(CustomUser, related_name='sent_food_connections',on_delete=models.CASCADE)
#     receiver = models.ForeignKey(CustomUser,related_name='received_food_connections',on_delete=models.CASCADE)
#     food_items = models.JSONField() 
#     location = models.CharField(max_length=300)
#     status = models.CharField(max_length=300)
#     accepted = models.BooleanField(default=False)
#     updated = models.DateTimeField(auto_now=True)
#     created = models.DateTimeField(auto_now_add=True)
    

#     def __str__(self):
#         return f'{self.sender.phone} -> {self.receiver.phone}'

class Message(models.Model):
    connection = models.ForeignKey(
        Connection,
        related_name='messages',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        CustomUser,
        related_name='my_messages',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.phone}: {self.text}'

class RideRequest(models.Model):
    rider = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ride_requests')
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='driver_requests')
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add any other fields as needed

    def __str__(self):
        return f'Ride request from {self.rider.phone} to {self.driver.phone} at ({self.latitude}, {self.longitude})'

class DriverOnline(models.Model):
    RIDE_TYPE_CHOICES = [
        ('CAR', 'Car'),
        ('MOTO', 'Motorcycle'),
        ('PACKAGE', 'Package Delivery'),
    ]
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_driver')
    phone = models.CharField(max_length=15, unique=True)
    ride_type = models.CharField(
        max_length=15,
        choices=RIDE_TYPE_CHOICES,
        default='CAR'
    )
    location = models.CharField(max_length=255,null=True, blank=True)
    latitude = models.CharField(max_length=255,null=True, blank=True)
    longitude = models.CharField(max_length=255,null=True, blank=True)
    is_online = models.BooleanField(default=False)  # New field
    push_token=  models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Driver {self.id} - {self.phone}"
