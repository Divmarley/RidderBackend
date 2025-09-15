from rest_framework import generics

from accounts import serializers
from accounts.models import CustomUser
from django.core.files.base import ContentFile
import base64
import uuid
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import CategorySerializer, RestaurantSerializer, FoodMenuSerializer, ReviewSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Category, OrderItem, Restaurant, Image, Rating, Location, FoodMenu, Review
from django.db.models import Sum, Count
from django.core.exceptions import ObjectDoesNotExist

class OrderAndFoodMenuCountView(APIView):
    def get(self, request):
 
        try:
            order_count = Order.objects.filter(receiver=request.user.id).count()
            food_menu_count = FoodMenu.objects.filter(restaurant=request.user).count()
            # print('food_menu_countxx',food_menu_count)
            # reviews_summary = Review.objects.filter(user=request.user.id,food_menu=food_menu_count).aggregate(
            #     total_reviews=Count('id'),
            #     accumulated_ratings=Sum('rating')
            # )
            return Response(
                {
                    'order_count': order_count,
                    'food_menu_count': food_menu_count,
                    # 'accumulated_ratings': reviews_summary.get('accumulated_ratings', 0) or 0
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print("error",e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryListView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter categories by restaurant (user) ID"""
        return Category.objects.filter(restaurant=self.request.user)
    
    def perform_create(self, serializer):
        """Add restaurant (user) when creating category"""
        serializer.save(restaurant=self.request.user)

class RestaurantListView(generics.ListAPIView):
    """
    View to list all restaurants for authenticated users.
    """
    queryset = Restaurant.objects.all()  # Ensure model name is correctly spelled
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]

 


    # def perform_create(self, serializer):
    #     # Extract nested data
    #     image_data = self.request.data.get('image')
    #     rating_data = self.request.data.get('rating')
    #     details_data = self.request.data.get('details')
    #     location_data = self.request.data.get('location')
    #     food_menu_data = self.request.data.get('food_menu', [])

    #     # Create nested objects
    #     image = Image.objects.create(**image_data) if image_data else None
    #     rating = Rating.objects.create(**rating_data) if rating_data else None
    #     details = Details.objects.create(**details_data) if details_data else None
    #     location = Location.objects.create(**location_data) if location_data else None

    #     # Create the Restaurant instance
    #     restaurant = serializer.save(
    #         user=self.request.user,
    #         image=image,
    #         rating=rating,
    #         details=details,
    #         location=location
    #     )

    #     # Create related FoodMenu items
    #     for food_item_data in food_menu_data:
    #         FoodMenu.objects.create(restaurant=restaurant, **food_item_data)

    #     # return restaurant
    
class RestaurantDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        return Restaurant.objects.all()

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return Restaurant.objects.get(user__id=user_id)
        except Restaurant.DoesNotExist:
            # Manually return a 404 Response
            self.response = Response(
                {"error": "Restaurant not found for the given user ID."},
                status=status.HTTP_404_NOT_FOUND
            )
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return self.response
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return self.response
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return self.response
        return super().destroy(request, *args, **kwargs)

# class FoodMenuCreate(generics.CreateAPIView):
#     queryset = FoodMenu.objects.all()
#     serializer_class = FoodMenuSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         try:
#             # Assuming the logged-in user's restaurant is tied to their account
#             print("self.request.user",self.request.user.id)
#             restaurant = Restaurant.objects.get(user= self.request.user.id)
             
          
#             serializer.save(restaurant=self.request.user)
#         except Restaurant.DoesNotExist:
#             raise serializers.ValidationError("No restaurant is associated with the current user.")

#     def create(self, request, *args, **kwargs):
#         """
#         Override the default create method to handle Base64-encoded image data.
#         """
#         if not request.data:
#             return Response(
#                 {"detail": "No data provided in the request."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Log request data for debugging
#         print("Request Data:", request.data)

#         # Check if 'image' is in the request and handle it
#         if 'image' in request.data:
#             image_data = request.data.get('image')
#             # Log the image data to check its format
#             print("Image Data:", image_data)
#             request.data['image'] = image_data  # Pass Base64 data to serializer

#         # Proceed with normal serializer validation and creation
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)

#         return Response(serializer.data, status=status.HTTP_201_CREATED)


import base64
from django.core.files.base import ContentFile

class FoodMenuCreate(generics.CreateAPIView):
    queryset = FoodMenu.objects.all()
    serializer_class = FoodMenuSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            # Get the restaurant associated with the user
            restaurant = self.request.user
            print(f"Creating food menu for user/restaurant: {restaurant}")
            
            # Save with the user as restaurant (since FoodMenu.restaurant points to CustomUser)
            serializer.save(restaurant=restaurant)
            
        except Exception as e:
            print(f"Error saving food menu: {str(e)}")
            raise serializers.ValidationError({
                "error": f"Error creating food menu: {str(e)}",
                "details": str(e)
            })

    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)
        
        try:
            # Prepare the data
            menu_data = {
                'name': request.data.get('name'),
                'description': request.data.get('description'),
                'price': request.data.get('price'),
                'category_id': request.data.get('category_id'),
                'order_type': request.data.get('order_type', ''),
                'free_addons': request.data.get('free_addons', []),
                'paid_addons': request.data.get('paid_addons', [])
            }

            # Handle image if present
            if 'image' in request.data:
                menu_data['image'] = request.data['image']
            # if 'image' in request.FILES:
            #     menu_data['image'] = request.FILES['image']

            # Create and validate serializer
            serializer = self.get_serializer(data=menu_data)
            
            if not serializer.is_valid():
                print("Validation errors:", serializer.errors)
                return Response({
                    "error": "Validation failed",
                    "details": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Save the food menu
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error in create: {str(e)}")
            return Response({
                "error": "Failed to create food menu",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


 

class FoodMenuList(generics.ListAPIView):
    serializer_class = FoodMenuSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # print(f"Getting food menu for user: {user.id}")
        
        try:
            if user.is_authenticated:
                # Try to get the restaurant
                restaurant = Restaurant.objects.filter(user=user).first()
                # print('restaurant',restaurant)
                if restaurant:
                    # print(f"Found restaurant: {restaurant.id}")
                    return FoodMenu.objects.filter(restaurant=user)
                else:
                    print("No restaurant found for user")
                    return FoodMenu.objects.none()
            else:
                print("User not authenticated")
                return FoodMenu.objects.none()
                
        except Exception as e:
            print(f"Error in get_queryset: {str(e)}")
            return FoodMenu.objects.none()


class UserFoodMenuList(generics.ListAPIView):
    serializer_class = FoodMenuSerializer
    permission_classes = [AllowAny]
 
    def get_queryset(self):
        user = self.request.user
        restaurant_id = self.kwargs.get('pk')  # Retrieve the `pk` from the URL
        
        print('restaurant_id',restaurant_id,user.is_authenticated)

        # if not user.is_authenticated:
        #     return FoodMenu.objects.none()  # Return empty queryset for unauthenticated users
        # restaurant = Restaurant.objects.all()
        # print('restaurant,restaurant',restaurant)
        try:
            # Get the restaurant object
            # restaurant = Restaurant.objects.get(user=restaurant_id)
            # print('restaurant===>',restaurant.restaurant)
            # Filter food menu by the restaurant 
            print('Restaurant', FoodMenu.objects.filter(restaurant=restaurant_id))
            return FoodMenu.objects.filter(restaurant=restaurant_id)
        except Restaurant.DoesNotExist:
            return FoodMenu.objects.none()  # Return empty queryset if the restaurant does not exist

class FoodMenuDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodMenu.objects.all()
    serializer_class = FoodMenuSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(user)
        return FoodMenu.objects.filter(restaurant=user)
    
    def delete(self, request, *args, **kwargs):
        """
        Override the delete method to add custom logic if necessary and ensure proper response.
        """
        instance = self.get_object()  # Get the specific object
        print("")
        print("Deleting food menu item:", instance) 
        self.perform_destroy(instance)
        return Response(
            {"message": "Food menu item deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.exceptions import NotFound 
from rest_framework.views import APIView

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(sender=self.request.user )
    

    # def create(self, request, *arrgs, **kwargs): 
    #     print(request.data)
    #     try:
    #         items_data = request.data.get('items', [])
    #         receiver_id = request.data.get('restaurant') 
    #         location = request.data.get('location')
    #         receiver = Restaurant.objects.get(id=receiver_id)
         
    #         sender =  request.user.id
    #         total_price = request.data.get('total_price')
            
    #         order_data = {
    #             'sender': sender,
    #             'receiver': receiver.id,
    #             'status': 'pending',
    #             'total_price': total_price,
    #             'items': items_data,
    #             'location':location
    #         }

    #         print("order_data", order_data)

    #         serializer = self.get_serializer(data=order_data)
    #         serializer.is_valid(raise_exception=True)
    #         order = serializer.save()

    #         # Send message via channels
    #         channel_layer = get_channel_layer()
    #         async_to_sync(channel_layer.group_send)(
    #             'orders', 
    #             {
    #                 'type': 'order_message',
    #                 'message': f'New order created: {order.id}'
    #             }
    #         )

    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     except Restaurant.DoesNotExist:
 
    #         return Response({'error': 'Receiver restaurant does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def create(self, request, *args, **kwargs):
        try:
            items_data = request.data.get('items', [])
            if not items_data:
                return Response({'error': 'No items provided for the order.'}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure all items have a valid item_id
            for item in items_data:
                if 'item_id' not in item or not item['item_id']:
                    return Response({'error': 'Item ID is required for all items.'}, status=status.HTTP_400_BAD_REQUEST)

            receiver_id = request.data.get('restaurant')
            location = request.data.get('location')
            receiver = Restaurant.objects.get(id=receiver_id)
            sender = request.user
            total_price = request.data.get('total_price')

            # Create the Order instance
            order = Order.objects.create(
                sender=sender,
                receiver=receiver,
                status='pending',
                total_price=total_price,
                location=location
            )

            # Create OrderItem instances
            for item_data in items_data:
                food_item = FoodMenu.objects.get(id=item_data['item_id'])
                OrderItem.objects.create(
                    order=order,
                    item=food_item,
                    quantity=item_data.get('quantity')
                )

            # Send message via channels
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'orders',
                {
                    'type': 'order_message',
                    'message': f'New order created: {order.id}'
                }
            )

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Restaurant.DoesNotExist:
            return Response({'error': 'Receiver restaurant does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except FoodMenu.DoesNotExist:
            return Response({'error': 'Food item does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Fetch orders where the user is the sender or receiver
        orders = Order.objects.filter(sender=user) | Order.objects.filter(receiver=user)
        
        # Prepare serialized orders data
        orders_data = []
        for order in orders:
            order_items = []
            for item in order.items.all():
                item_data = {
                    "item_id": item.food_menu.id,
                    "quantity": item.quantity,
                    "name": item.food_menu.name,
                    "description": item.food_menu.description,
                    "price": float(item.food_menu.price)
                }
                order_items.append(item_data)

            orders_data.append({
                "order_id": order.id,
                "status": order.status,
                "location": order.location,
                "total_price": float(order.total_price),
                "items": order_items
            })

        return Response({'orders': orders_data})
    
class OrderListByIdView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        order_id = self.kwargs.get('id')
        return Order.objects.filter(id=order_id,sender=self.request.user )
    

class OrderAcceptView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.receiver != request.user:
            return Response({'error': 'You can only accept orders sent to you.'}, status=status.HTTP_403_FORBIDDEN)
        instance.status = 'accepted'
        instance.save()
        return Response(self.get_serializer(instance).data)

class OrderDeclineView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.receiver != request.user:
            return Response({'error': 'You can only decline orders sent to you.'}, status=status.HTTP_403_FORBIDDEN)
        instance.status = 'declined'
        instance.save()
        return Response(self.get_serializer(instance).data)
    

class OrderStatusView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('id')
        try:
            order = Order.objects.get(id=order_id)
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            raise NotFound('Order not found')
        

class ReviewCreateView(APIView):
    def post(self, request, food_menu_id):
        food_menu = get_object_or_404(FoodMenu, id=food_menu_id)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(food_menu=food_menu, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewCountView(APIView):
    def get(self, request, food_menu_id):
        food_menu = get_object_or_404(FoodMenu, id=food_menu_id)
        review_count = food_menu.reviews.count()
        return Response({'food_menu': food_menu.name, 'review_count': review_count})


@api_view(['POST'])
def create_restaurant(request):
    try:
        # Get the authenticated user
        user = request.user
        if not user.is_authenticated:
            return Response({
                "status": "error",
                "code": "authentication_required",
                "message": "Authentication is required to create a restaurant"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Validate required fields
        required_fields = ['name', 'price_range', 'delivery_time', 'address', 'city', 'country']
        missing_fields = [field for field in required_fields if not request.data.get(field)]
        if missing_fields:
            return Response({
                "status": "error",
                "code": "missing_fields",
                "message": "Required fields are missing",
                "fields": missing_fields
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if restaurant already exists for user
        if Restaurant.objects.filter(user=user).exists():
            return Response({
                "status": "error",
                "code": "restaurant_exists",
                "message": "User already has a restaurant registered"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract data from request
        data = request.data
        
        try:
            # Create restaurant
            restaurant = Restaurant.objects.create(
                user=user,
                name=data.get('name'),
                price_range=data.get('price_range'),
                delivery_time=data.get('delivery_time'),
                address=data.get('address'),
                city=data.get('city'),
                country=data.get('country'),
                coordinates=data.get('coordinates', {}),
                rating=data.get('rating', 0),
                cuisine=data.get('cuisine', ''),
                about_us=data.get('about_us', ''),
                delivery_fee=data.get('delivery_fee', 0.0)
            )

            # Handle image if provided
            if 'image' in request.FILES:
                restaurant.image = request.FILES['image']
                restaurant.save()

            return Response({
                "status": "success",
                "message": "Restaurant created successfully",
                "data": {
                    "restaurant_id": restaurant.id,
                    "name": restaurant.name,
                    "address": restaurant.address
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({
                "status": "error",
                "code": "creation_failed",
                "message": "Failed to create restaurant",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            "status": "error",
            "code": "server_error",
            "message": "An unexpected error occurred",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Restaurant
from .serializers import RestaurantNewSerializer

''' sammple data 
{
  "id": 1,
  "name": "Pizza Palace",
  "image_main": "https://images.unsplash.com/photo-1513104890138-7c749659a591",
  "image_featured": [
    "https://images.unsplash.com/photo-1513104890138-7c749659a591",
    "https://images.unsplash.com/photo-1513104890138-7c749659a591"
  ],
  "rating": 4.5,
  "delivery_time": "25-30 mins",
  "cuisine": "Italian",
  "promoted": false,
  "open": true,
  "about_us": "Best Italian Pizza in town.",
  "delivery_modes": ["delivery", "pickup"],
  "location": {
    "address": "123 Pizza Lane",
    "city": "Naples",
    "country": "Italy",
    "latitude": 40.8518,
    "longitude": 14.2681
  },
  "contact": [
    {"type": "call", "value": "024444444"},
    {"type": "email", "value": "demo@example.com"},
    {"type": "website", "value": "www.pizzapalace.com"}
  ],
  "delivery_fee": "23.00",
  "most_popular": [
    {"id": 1, "name": "Margherita Pizza", "price": "8.99"},
    {"id": 2, "name": "Pepperoni Pizza", "price": "10.99"}
  ],
  "price_range": "$2-$5",
  "operational_hours": {
    "weekdays": {"open": "10:00 AM", "close": "10:00 PM"},
    "weekends": {"open": "9:00 AM", "close": "11:00 PM"}
  },
  "payment_options": ["Cash", "Credit Card", "PayPal"],
  "categories": ["Pizza", "Pasta"]
}

'''
class RestaurantAPIView(APIView):
 
    def get(self, request):
        restaurants = Restaurant.objects.filter(user__is_aproved=True)
        print("Getting",restaurants )
    
        serializer = RestaurantNewSerializer(restaurants, many=True)
        # print("Serializing",serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request): 
        serializer = RestaurantNewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        print('serializer.errors',serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# add get Restaurant based on userid 

@api_view(['GET'])
def get_restaurant_by_id(request, pk):
    try:
        restaurant = Restaurant.objects.get(user=pk)
        serializer = RestaurantNewSerializer(restaurant)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Restaurant.DoesNotExist:
     
        return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)