from django.contrib import admin
from .models import Restuarant, Image, Rating, Location, Details, FoodMenu
 
# from .models import FoodOrder

# admin.site.register(FoodOrder)


admin.site.register(Restuarant)
admin.site.register(Image)
admin.site.register(Rating)
admin.site.register(Location)
admin.site.register(Details)
admin.site.register(FoodMenu)
