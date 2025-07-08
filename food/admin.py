from django.contrib import admin
from .models import Restaurant, Image, Rating, Location, FoodMenu
 
# from .models import FoodOrder

# admin.site.register(FoodOrder)


admin.site.register(Restaurant)
admin.site.register(Image)
admin.site.register(Rating)
admin.site.register(Location)
 
admin.site.register(FoodMenu)
