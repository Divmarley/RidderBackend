from rest_framework import generics

from accounts.models import CustomUser
from django.core.files.base import ContentFile
import base64
import uuid

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import CategorySerializer, RestaurantSerializer, FoodMenuSerializer, ReviewSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Category, OrderItem, Restaurant, Image, Rating, Details, Location, FoodMenu, Review
from django.db.models import Sum, Count

class OrderAndFoodMenuCountView(APIView):
    def get(self, request):
        try:
            order_count = Order.objects.count()
            food_menu_count = FoodMenu.objects.count()
            reviews_summary = Review.objects.filter(food_menu=food_menu_count).aggregate(
                total_reviews=Count('id'),
                accumulated_ratings=Sum('rating')
            )
            return Response(
                {
                    'order_count': order_count,
                    'food_menu_count': food_menu_count,
                    'accumulated_ratings': reviews_summary.get('accumulated_ratings', 0) or 0
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantList(generics.ListCreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


class CategoryListView(ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant_id = self.request.user.id
        # print("restaurant_id", restaurant_id)
        if restaurant_id:
            cat= Category.objects.all()
            # cat= Category.objects.filter(restaurant_id=restaurant_id)
            print( "cat", cat)
            return cat
        return Category.objects.all()

class RestaurantListCreateView(generics.ListCreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        # Extract nested data
        image_data = self.request.data.get('image')
        rating_data = self.request.data.get('rating')
        details_data = self.request.data.get('details')
        location_data = self.request.data.get('location')
        food_menu_data = self.request.data.get('food_menu', [])

        # Create nested objects
        image = Image.objects.create(**image_data) if image_data else None
        rating = Rating.objects.create(**rating_data) if rating_data else None
        details = Details.objects.create(**details_data) if details_data else None
        location = Location.objects.create(**location_data) if location_data else None

        # Create the Restaurant instance
        restaurant = serializer.save(
            user=self.request.user,
            image=image,
            rating=rating,
            details=details,
            location=location
        )

        # Create related FoodMenu items
        for food_item_data in food_menu_data:
            FoodMenu.objects.create(restaurant=restaurant, **food_item_data)

        return restaurant
    
class RestaurantDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class FoodMenuCreate(generics.CreateAPIView):
    queryset = FoodMenu.objects.all()
    serializer_class = FoodMenuSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Set the restaurant field to the current user
        a=  Restaurant.objects.get(user=self.request.user.id)

        print("a",a)
        serializer.save(restaurant=a)

    def create(self, request, *args, **kwargs):
        """
        Override the default create method to handle Base64-encoded image data.
        """
        if not request.data:
            return Response(
                {"detail": "No data provided in the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log request data for debugging
        print("Request Data:", request.data)

        # Check if 'image' is in the request and handle it
        if 'image' in request.data:
            image_data = request.data.get('image')
            # Log the image data to check its format
            print("Image Data:", image_data)
            request.data['image'] = image_data  # Pass Base64 data to serializer

        # Proceed with normal serializer validation and creation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FoodMenuList(generics.ListAPIView):
    serializer_class = FoodMenuSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
 

        # Filter by restaurant_id and, optionally, user
         
        if user.is_authenticated:
            return FoodMenu.objects.filter(restaurant=user.id, )
        # return FoodMenu.objects.filter(restaurant_id=restaurant_id)
    
        return FoodMenu.objects.none()

class FoodMenuDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodMenu.objects.all()
    serializer_class = FoodMenuSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FoodMenu.objects.filter(restaurant__user=user)
    
    def delete(self, request, *args, **kwargs):
        """
        Override the delete method to add custom logic if necessary and ensure proper response.
        """
        instance = self.get_object()  # Get the specific object
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