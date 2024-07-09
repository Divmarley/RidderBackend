from django.contrib import admin
from .models import Restaurant, Image, Rating, Location, Details, FoodMenu

admin.site.register(Restaurant)
admin.site.register(Image)
admin.site.register(Rating)
admin.site.register(Location)
admin.site.register(Details)
admin.site.register(FoodMenu)
