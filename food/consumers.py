from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from accounts.models import CustomUser
import json
from asgiref.sync import async_to_sync
from food.models import FoodConnection, FoodMenu, Order, OrderItem,Restaurant
from food.serializers import OrderSerializer, RequestFoodSerializer



class FoodConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
           self.close()

        self.room_name = f"food_{self.user.id}"
        self.room_group_name = f"food_{self.user.id}"

        self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    
    def disconnect(self, close_code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    
    def receive(self, text_data):
        data = json.loads(text_data)
        data_source = data.get('source')
        # print('FoodConsumer Received message:', json.dumps(data, indent=2))

        if data_source == 'request.connect.food':
            self.receive_food_request_connect(data)
        elif data_source == 'foodOrder.list':
            self.receive_food_list(data)
        elif data_source == 'list.orders':
            self.list_orders()
        
    
    def receive_food_request_connect(self, data):
        daseData = data.get('data')

        location = daseData['location']
        phone = daseData['phone']
        restaurant_id = daseData['restaurant']
        pushToken = daseData['pushToken']
        items = daseData['items']
        total_price = daseData['total_price']
        status = daseData['status']
        user = self.scope['user']

        if not user:
            self.send(text_data=json.dumps({
                'error': 'User is not authenticated'
            }))
            return

        try:
            restaurant = CustomUser.objects.get(id=restaurant_id)
        except CustomUser.DoesNotExist:
            self.send(text_data=json.dumps({
                'error': 'Restaurant not found'
            }))
            return

        # Create or retrieve FoodConnection instance
        connection, _ = FoodConnection.objects.get_or_create(
            buyer=user,  # Use the authenticated user
            restaurant=restaurant,
            location=location,
            pushToken=pushToken,
            defaults={'items': items}  # Store items as needed
        )

        # Create Order instance
        order = Order.objects.create(
            sender=connection.buyer,
            receiver=connection.restaurant,
            status=status,
            location=connection.location,
            total_price=total_price
        )

        # Create OrderItem instances for each item in the order
        for item_data in items:
            item_id = item_data.get('item_id')
            quantity = item_data.get('quantity')

            try:
                food_item = FoodMenu.objects.get(id=item_id)
                OrderItem.objects.create(
                    order=order,
                    food_menu=food_item,  # Ensure this is the correct field name
                    quantity=quantity
                )
            except FoodMenu.DoesNotExist:
                print(f"Food item with id {item_id} not found")

        # Serialize connection and send back to sender and receiver
        serialized = RequestFoodSerializer(connection)

        self.send_group(
            connection.buyer.phone, 'request.connect.food', serialized.data
        )
        self.send_group(
            connection.restaurant.phone, 'request.connect.food', serialized.data
        )

    def list_orders(self):
        user = self.scope['user']
        if not user:
            self.send(text_data=json.dumps({
                'source': 'list.orders',
                'error': 'User is not authenticated'
            }))
            return

        # Fetch orders where the user is the sender or receiver
        orders = Order.objects.filter(
            sender=user
        ) | Order.objects.filter(receiver=user)

        # Prepare serialized orders data with item details
        orders_data = []
        for order in orders:
            # Fetch items related to the order
            order_items = []
            for item in order.items.all():
                item_data = {
                    "item_id": item.food_menu.id,  # Corrected here
                    "quantity": item.quantity,
                    "name": item.food_menu.name,
                    "description": item.food_menu.description,
                    "price": float(item.food_menu.price)  # Convert Decimal to float
                }
                order_items.append(item_data)

            # Add order details including item data
            orders_data.append({
                "order_id": order.id,
                "status": order.status,
                "location": order.location,
                "total_price": float(order.total_price),  # Convert Decimal to float
                "items": order_items
            })

        # Send back the detailed orders list to the client
        response_data = {
            'source': 'list.orders',
            'status': 'success',
            'orders': orders_data
        }

        # Send serialized data back to the client
        self.send(text_data=json.dumps(response_data))

        # self.send_group(
		# 	connection.sender.phone, 'trip.start', serialized.data
		# )


    def receive_food_list(self, data):
        user = self.scope['user']
        if not user:
            self.send(text_data=json.dumps({
                'error': 'User is not authenticated'
            }))
            return
        print("receive_food_list", data)
        print("receive_request_connect data",data)
		# Attempt to fetch the receiving user
        # try:
        #     resturant = CustomUser.objects.get(phone='233262639764')
        # except CustomUser.DoesNotExist:
        #     print('Error: User not found')
        #     return
		# # Create connection
        # connection, _ = FoodConnection.objects.get_or_create(
		# 	sender=self.scope['user'],
		# 	receiver=resturant,
		# 	location='accra',
		# 	pushToken= "push_token"
		# )

        # print("connection",connection)
		
    # def receive_create_food_order(self, data):
    #     phone = data.get('phone')
    #     print("receive_create_food_order", data)
    #     user = self.scope['user']
    #     if not user:
    #         self.send(text_data=json.dumps({
    #             'error': 'User is not authenticated'
    #         }))
    #         return
 
	# 	# Attempt to fetch the receiving user
    #     try:
    #         resturant = CustomUser.objects.get(phone=phone)
    #     except CustomUser.DoesNotExist:
    #         print('Error: User not found')
    #         return
	# 	# Create connection
    #     connection, _ = FoodConnection.objects.get_or_create(
	# 		sender=self.scope['user'],
	# 		receiver=resturant,
	# 		location='accra',
	# 		pushToken= "push_token"
	# 	)

    #     print("connection",connection)
        
    def send_group(self, group, source, data):
        response = {
            'type': 'broadcast_group',
            'source': source,
            'data': data
        }
        async_to_sync(self.channel_layer.group_send)(
            group, response
        )

    def broadcast_group(self, data):
        '''
        data:
            - type: 'broadcast_group'
            - source: where it originated from
            - data: what ever you want to send as a dict
        '''
        data.pop('type')
        '''
        return data:
            - source: where it originated from
            - data: what ever you want to send as a dict
        '''
        self.send(text_data=json.dumps(data))
        




    
    