from django.db import models
from accounts.models import CustomUser

class Image(models.Model):
    uri = models.URLField()
    border_radius = models.IntegerField(null=True, blank=True)  # Optional field

    def __str__(self):
        return f"Image {self.uri}"

class Rating(models.Model):
    value = models.FloatField()
    number_of_ratings = models.IntegerField(null=True, blank=True)  # Optional field

    def __str__(self):
        return f"Rating {self.value} ({self.number_of_ratings} ratings)"

class Location(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.country}"

class Details(models.Model):
    name = models.CharField(max_length=100)
    price_range = models.CharField(max_length=100)
    delivery_time = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.price_range} - {self.delivery_time}"

class FoodMenu(models.Model):
    # restaurant = models.ForeignKey('Restaurant', related_name='food_menu', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    image = models.URLField()

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    user = models.ForeignKey(CustomUser, related_name='restaurant_owner', on_delete=models.CASCADE)
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
    is_open = models.BooleanField(default=False)
    about_us = models.TextField(null=True, blank=True)
    delivery_fee = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.details.name

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
    location = models.CharField(max_length=300)
    total_price = models.FloatField()

    def __str__(self):
        return f"Order from {self.sender.username} to {self.receiver.details.name} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item_id = models.ForeignKey(FoodMenu, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"OrderItem {self.id} for Order {self.order.id}: {self.item_id.name}"
