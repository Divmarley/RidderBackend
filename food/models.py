from django.db import models
from accounts.models import CustomUser

from django.db.models.signals import pre_save
from django.dispatch import receiver


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
    order_info= models.JSONField()
   
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
    coordinates = models.JSONField()

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

from django.db import models
import json

# Category model for food items
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    restaurant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="categories")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

'''
{
    foodCategory: 'breakfast',
    name: 'Laos',
    description: 'This',
    free_addons: [],
    id: 1,
    image:
      'file:///var/mobile/Containers/Data/Application/6A1CEE42-0A06-41FF-9556-5C6195E21F47/tmp/5043479C-9116-488E-9743-CB4C57F3E08A.png',
    order_type: 'delivery',
    paid_addons: [],
    price: '23.00',
    description: 'lorem ipsum dolor sit',
  }

  {
    "category": 1, 
    "description": "Bdb", 
    "free_addons": [], 
    "id": 2, 
    "image": "file:///var/mobile/Containers/Data/Application/DBA06034-242B-4128-8DFD-99C954075099/tmp/83C5BD71-36D3-41A4-B98F-FA7313587C3F.jpg", 
    "name": "Booker", 
    "order_type": "delivery", 
    "paid_addons": [],
    "price": "12.00"
   }
  '''
class FoodMenu(models.Model):
    restaurant = models.ForeignKey(CustomUser, related_name="user_food_menu", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="food_items", on_delete=models.CASCADE)  # Link to Category
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='food_menu_images/', blank=True, null=True,max_length=5000)
    # image = models.ImageField(upload_to='food_menu/')
    order_type = models.CharField(max_length=50)
    free_addons = models.JSONField(default=list)
    paid_addons = models.JSONField(default=list)
    def __str__(self):
        return f"{self.name} - {self.category.name}"

# class Restaurant(models.Model):
#     user = models.ForeignKey(CustomUser, related_name='restaurants', on_delete=models.CASCADE)
#     AVAILABLE_CHOICES = [
#         ('open', 'Open'),
#         ('closed', 'Closed'),
#     ]
#     available = models.CharField(max_length=6, choices=AVAILABLE_CHOICES)
#     # image = models.OneToOneField(Image, on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='images/')
#     rating = models.OneToOneField(Rating, on_delete=models.CASCADE)
#     details = models.OneToOneField(Details, on_delete=models.CASCADE)
#     location = models.OneToOneField(Location, on_delete=models.CASCADE)
 
#     cuisine = models.CharField(max_length=255)
#     is_open = models.BooleanField(default=False)
#     about_us = models.TextField(null=True, blank=True)
#     delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

#     def __str__(self):
#         return self.details.name

#     class Meta:
#         verbose_name = "Restaurant"
#         verbose_name_plural = "Restaurants"

AVAILABLE_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
class Restuarant(models.Model):
    user = models.ForeignKey(CustomUser, related_name='restaurants', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price_range = models.CharField(max_length=100)
    delivery_time = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    coordinates = models.JSONField() 
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    rating = models.IntegerField(default=0)
    cuisine = models.CharField(max_length=255)
    is_open = models.BooleanField(default=True)
    about_us = models.TextField(null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"
 
import random
import string

def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('handed_over', 'Handed Over to Rider'),
        ('on_the_way', 'On the Way to Destination'),
        ('delivered', 'Delivered'),
    ]
    order_id = models.CharField(max_length=10, unique=True, editable=False)
    sender = models.ForeignKey(CustomUser, related_name='sent_orders', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_orders', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=300)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    food_connection_id=models.PositiveIntegerField()

    def __str__(self):
        return f"Order from {self.sender.name} to {self.receiver.name} - {self.status}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

# Signal to automatically generate order ID before saving
@receiver(pre_save, sender=Order)
def set_order_id(sender, instance, **kwargs):
    if not instance.order_id:
        instance.order_id = generate_order_id()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)  # Use related_name='items'
    food_menu = models.ForeignKey(FoodMenu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"OrderItem {self.id} for Order {self.order.id}: {self.item.name}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class Review(models.Model):
    food_menu = models.ForeignKey('FoodMenu', related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # E.g., 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.name} on {self.food_menu.name}"
    


# ===========================new============================

class Location(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.country}"

class Contact(models.Model):
    type = models.CharField(max_length=50)  # e.g., call, email, website
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.type}: {self.value}"

class Restaurant(models.Model):
    user = models.ForeignKey(CustomUser, related_name='restaurant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image_main = models.TextField()
    image_featured = models.JSONField()  # List of image URLs
    rating = models.FloatField()
    delivery_time = models.CharField(max_length=50)  # e.g., '25-30 mins'
    cuisine = models.CharField(max_length=100)
    promoted = models.BooleanField(default=False)
    open = models.BooleanField(default=True)
    about_us = models.TextField()
    delivery_modes = models.JSONField()  # e.g., ['delivery', 'pickup']
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    contact = models.ManyToManyField(Contact)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    most_popular = models.JSONField(default=list)  # [{id, name, price}]
    price_range = models.CharField(max_length=20)
    operational_hours = models.JSONField()  # e.g., {"weekdays": {"open": "10:00", "close": "22:00"}}
    payment_options = models.JSONField()  # e.g., ['Cash', 'Credit Card', 'PayPal']
    categories = models.JSONField()  # e.g., ['Pizza', 'Pasta']

    def __str__(self):
        return self.name

class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='reviews', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.user_name} - {self.restaurant.name}"

class Promotion(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='promotions', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title
