from django.db import models
from accounts.models import CustomUser



class FoodConnection(models.Model):
    buyer = models.ForeignKey(
        CustomUser,
        related_name='buyer_sent_connections',
        on_delete=models.CASCADE
    )
    location = models.JSONField()
    status = models.CharField(max_length=300)
    restaurant = models.ForeignKey(
        CustomUser,
        related_name='restaurant_received_connections',
        on_delete=models.CASCADE
    )
    pushToken= models.CharField(max_length=2000)
    items= models.JSONField()
    
    # pushToken= models.CharField(max_length=2000)
   
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f'{self.buyer.phone} -> {self.restaurant.phone}'
    

class Image(models.Model):
    uri = models.URLField()
    border_radius = models.IntegerField(null=True, blank=True)  # Optional field

    def __str__(self):
        return f"Image {self.uri}"

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

class Rating(models.Model):
    value = models.FloatField()
    number_of_ratings = models.IntegerField(null=True, blank=True)  # Optional field

    def __str__(self):
        return f"Rating {self.value} ({self.number_of_ratings} ratings)"

    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"

class Location(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.country}"

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

class Details(models.Model):
    name = models.CharField(max_length=100)
    price_range = models.CharField(max_length=100)
    delivery_time = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.price_range} - {self.delivery_time}"

    class Meta:
        verbose_name = "Details"
        verbose_name_plural = "Details"

class FoodMenu(models.Model):
    restaurant = models.ForeignKey('Restaurant', related_name='food_menu', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Food Menu"
        verbose_name_plural = "Food Menus"

class Restaurant(models.Model):
    user = models.ForeignKey(CustomUser, related_name='restaurants', on_delete=models.CASCADE)
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
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.details.name

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"

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
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order from {self.sender.name} to {self.receiver.details.name} - {self.status}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(FoodMenu, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"OrderItem {self.id} for Order {self.order.id}: {self.item.name}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
