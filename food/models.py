from django.db import models

from accounts.models import CustomUser

class Image(models.Model):
    uri = models.URLField()
    border_radius = models.IntegerField()

class Rating(models.Model):
    value = models.FloatField()
    number_of_ratings = models.IntegerField(null=True, blank=True)

class Location(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

class Details(models.Model):
    name = models.CharField(max_length=100)
    price_range = models.CharField(max_length=100)
    delivery_time = models.CharField(max_length=50)

class FoodMenu(models.Model):
    restaurant = models.ForeignKey('Restaurant', related_name='food_menu', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    image = models.URLField()

class Restaurant(models.Model):
    user= models.ForeignKey(CustomUser, related_name='restaurant_owner', on_delete  = models.CASCADE)   # TODO  
    AVAILABLE_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    available = models.CharField(max_length=6, choices=AVAILABLE_CHOICES)
    image = models.OneToOneField(Image, on_delete=models.CASCADE)
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE)
    details = models.OneToOneField(Details, on_delete=models.CASCADE)
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    cuisine = models.CharField(max_length=255)
    is_open = models.BooleanField()
    about_us = models.TextField(null=True, blank=True)
    delivery_fee = models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.user.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('handed_over', 'Handed Over to Rider'),
        ('on_the_way', 'On the Way to Destination'),
        ('delivered', 'Delivered'),
    ]
    
    
    sender = models.ForeignKey(CustomUser, related_name='sent_orders', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Restaurant, related_name='received_orders', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # restaurant = models.ForeignKey(Restaurant, related_name='orders', on_delete=models.CASCADE)
    # food_items = models.ManyToManyField(FoodMenu, related_name='orders')
    location= models.CharField(max_length=300)
    total_price = models.FloatField()

    # def __str__(self):
    #     return f'Order from {self.sender} to {self.receiver} - {self.status}'
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item_id = models.ForeignKey(FoodMenu, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f'OrderItem {self.id} for Order {self.order.id}: {self.item_id.name}'
    


# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class FoodOrder(models.Model):  
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


#     def __str__(self):
#         return f"Food Order for {self.sender.name} - to {self.receiver.name}"
