from rest_framework import serializers

from accounts.models import CustomUser
from .models import Category, OrderItem, Restaurant, Image, Rating, Location, Details, FoodMenu,FoodConnection, Review

from rest_framework.exceptions import ValidationError

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class FoodConnectionSerializer(serializers.ModelSerializer):
    
    buyer = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    restaurant = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    items = serializers.JSONField()
    location = serializers.JSONField()
    
    class Meta:
        model = FoodConnection
        fields = ['id', 'buyer', 'restaurant', 'location', 'status', 'pushToken', 'items', 'updated', 'created']


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
        fields = ['address', 'city', 'country','coordinates']

class DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details
        fields = ['name', 'price_range', 'delivery_time']

class FoodMenuSerializer(serializers.ModelSerializer):
    # category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Category as a PrimaryKey
    category =  serializers.CharField(source='category.name', read_only=True)  # Category as a PrimaryKey
    order_type = serializers.CharField(max_length=50)  # New field: order_type
    free_addons = serializers.JSONField()  # New field: free_addons (expects a JSON list)
    paid_addons = serializers.JSONField()  # New field: paid_addons (expects a JSON list)
    image = serializers.CharField()  # Accepts a Base64 string
    class Meta:
        model = FoodMenu
        fields = ['id', 'name', 'description', 'price', 'image', 'order_type', 'free_addons', 'paid_addons','category']
        read_only_fields = ['id']

    # Handle unique constraint validation on the name field
    def validate_name(self, value):
        # Check if a food menu item with the same name already exists (excluding the current instance if updating)
        if FoodMenu.objects.filter(name=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise ValidationError("A food menu item with this name already exists.")
        return value

class RestaurantSerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    rating = RatingSerializer()
    details = DetailsSerializer()
    location = LocationSerializer()
    food_menu = FoodMenuSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        # fields = ['id', 'available', 'image', 'rating', 'details', 'location', 'cuisine', 'is_open', 'food_menu', 'about_us', 'delivery_fee']
        fields = ['id','user', 'available', 'image', 'rating', 'details', 'location', 'cuisine', 'is_open', 'about_us', 'delivery_fee','food_menu']

    def create(self, validated_data):
        image_data = validated_data.pop('image')
        rating_data = validated_data.pop('rating')
        details_data = validated_data.pop('details')
        location_data = validated_data.pop('location')
        # food_menu_data = validated_data.pop('food_menu')

        image = Image.objects.create(**image_data)
        rating = Rating.objects.create(**rating_data)
        details = Details.objects.create(**details_data)
        location = Location.objects.create(**location_data)
        
        restaurant = Restaurant.objects.create(image=image, rating=rating, details=details, location=location, **validated_data)

        # for food_item in food_menu_data:
        #     FoodMenu.objects.create(restaurant=restaurant, **food_item)
        
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
from .models import Order, OrderItem,FoodConnection
from accounts.serializers import UserSerializer

class RequestFoodSerializer(serializers.ModelSerializer):
    buyer = UserSerializer()
    restaurant = UserSerializer()

    class Meta:
        model = FoodConnection
        fields = [
            'id',
            'buyer',
            'restaurant',
            'location',
            'created',
            'status',
            'items'
            # 'data_driver'

        ]

        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'food_menu', 'quantity']  # Change 'item' to 'food_menu'


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
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_at']