from rest_framework import serializers
from .models import OrderItem, Restaurant, Image, Rating, Location, Details, FoodMenu

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['uri', 'border_radius']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['value', 'number_of_ratings']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['address', 'city', 'country']

class DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details
        fields = ['name', 'price_range', 'delivery_time']

class FoodMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodMenu
        fields = ['id','restaurant', 'name', 'description', 'price', 'image']
        read_only_fields = ['id']

class RestaurantSerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    rating = RatingSerializer()
    details = DetailsSerializer()
    location = LocationSerializer()
    food_menu = FoodMenuSerializer(many=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'available', 'image', 'rating', 'details', 'location', 'cuisine', 'is_open', 'food_menu', 'about_us', 'delivery_fee']

    def create(self, validated_data):
        image_data = validated_data.pop('image')
        rating_data = validated_data.pop('rating')
        details_data = validated_data.pop('details')
        location_data = validated_data.pop('location')
        food_menu_data = validated_data.pop('food_menu')

        image = Image.objects.create(**image_data)
        rating = Rating.objects.create(**rating_data)
        details = Details.objects.create(**details_data)
        location = Location.objects.create(**location_data)
        
        restaurant = Restaurant.objects.create(image=image, rating=rating, details=details, location=location, **validated_data)

        for food_item in food_menu_data:
            FoodMenu.objects.create(restaurant=restaurant, **food_item)
        
        return restaurant

    def update(self, instance, validated_data):
        image_data = validated_data.pop('image', None)
        rating_data = validated_data.pop('rating', None)
        details_data = validated_data.pop('details', None)
        location_data = validated_data.pop('location', None)
        food_menu_data = validated_data.pop('food_menu', None)

        if image_data:
            for attr, value in image_data.items():
                setattr(instance.image, attr, value)
            instance.image.save()

        if rating_data:
            for attr, value in rating_data.items():
                setattr(instance.rating, attr, value)
            instance.rating.save()

        if details_data:
            for attr, value in details_data.items():
                setattr(instance.details, attr, value)
            instance.details.save()

        if location_data:
            for attr, value in location_data.items():
                setattr(instance.location, attr, value)
            instance.location.save()

        if food_menu_data:
            instance.food_menu.all().delete()
            for food_item in food_menu_data:
                FoodMenu.objects.create(restaurant=instance, **food_item)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


 
from .models import Order


from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['item_id', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id','sender', 'receiver','location', 'status', 'items', 'total_price','updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order