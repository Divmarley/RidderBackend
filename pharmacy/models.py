from django.db import models

from accounts.models import CustomUser
from food.models import *
from food.models import *
 

# Create your models here.
class Pharmacy(models.Model):
    user = models.ForeignKey(CustomUser, related_name='pharmacy', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image_main = models.TextField()
    image_featured = models.JSONField()  # List of image URLs
    rating = models.FloatField()
    delivery_time = models.CharField(max_length=50)  # e.g., '25-30 mins'
    promoted = models.BooleanField(default=False)
    open = models.BooleanField(default=True)
    about_us = models.TextField()
    delivery_modes = models.JSONField()  # e.g., ['delivery', 'pickup']
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    contact = models.ManyToManyField(Contact)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    operational_hours = models.JSONField()  # e.g., {"weekdays": {"open": "10:00", "close": "22:00"}}
    payment_options = models.JSONField()  # e.g., ['Cash', 'Credit Card', 'PayPal']
    categories =models.JSONField()

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Pharmacy'
        managed = True
        verbose_name = 'Pharmacy'
        verbose_name_plural = 'Pharmacys'

class PharmacyCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    pharmacy_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="pharmacy_category_user")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Pharmacy Category"
        verbose_name_plural = "Pharmacy Categories"

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

class PharmacyProduct(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, related_name="pharmacy_product", on_delete=models.CASCADE)
    # category = models.ForeignKey(PharmacyCategory, related_name="pharmacy_product_category", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='pharmacy/product/', blank=True, null=True, max_length=5000)
    order_type = models.CharField(max_length=50)
    inStock = models.BooleanField(default=True)
    requiresPrescription = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - "#{self.category.name}

    class Meta:
        db_table = 'PharmacyProduct'
        managed = True
        verbose_name = 'Pharmacy Product'
        verbose_name_plural = 'Pharmacy Products'
