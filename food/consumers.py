from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from accounts.models import CustomUser
import json
from asgiref.sync import async_to_sync
from food.models import FoodConnection, FoodMenu, Order, OrderItem,Restaurant
from food.serializers import FoodConnectionSerializer, OrderSerializer, RequestFoodSerializer



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
        print('FoodConsumer Received message:', json.dumps(data, indent=2))

        if data_source == 'request.connect.food':
            self.receive_food_request_connect(data)
        elif data_source == 'foodOrder.list':
            self.receive_food_list(data)
        elif data_source == 'list.orders':
            self.list_orders()
        elif data_source == 'update.order.status':
            self.update_order_status(data)

    

    def update_order_status(self, data):
        print("data",data)
        """
        Function to update the order and FoodConnection status.
        """
        food_connection_id = data.get('foodConnectionId')
        new_status = data.get('status')
        order_id = data.get('order_id')
        # print('order_id=====?:', order_id,food_connection_id)
        user = self.scope['user']


        if not user:
            self.send(text_data=json.dumps({
                'error': 'User is not authenticated'
            }))
            return

        try:
            food_connection = FoodConnection.objects.get(id=food_connection_id)
        except FoodConnection.DoesNotExist:
            self.send(text_data=json.dumps({
                'error': 'Food connection not found'
            }))
            return

        # Ensure that the user is either the buyer or the restaurant involved in the connection
        if food_connection.buyer != user and food_connection.restaurant != user:
            self.send(text_data=json.dumps({
                'error': 'You are not authorized to update this order'
            }))
            return

        # Fetch the related order
        try:
            orders = Order.objects.filter(sender=food_connection.buyer, receiver=food_connection.restaurant,order_id =order_id)
         
        except Order.DoesNotExist:
            self.send(text_data=json.dumps({
                'error': 'Order not found for the provided connection'
            }))
            return
       
        
        updated_orders = []
        for order in orders:
            order.status = data['status']
            order.save()
            updated_orders.append({
                'id': order.id,
                'status': order.status,
                'updated_at': order.updated_at.isoformat(),  # Example of sending back the updated time
            })
 

        # Update the FoodConnection status (this can be the same status as the order, or it can be something different)
        food_connection.status = new_status
        food_connection.save()
        

        # Serialize the updated order and food connection
        order_data = OrderSerializer(order).data
        print("order_data==>",order_data)
        food_connection_data = FoodConnectionSerializer(food_connection).data
        

        # Notify both the buyer (sender) and restaurant (receiver) about the status update
        print("food_connection_data",food_connection_data)
        self.send_group(
            food_connection.buyer.phone, 'update.order.status',  food_connection_data
        )
        self.send_group(
            food_connection.restaurant.phone, 'update.order.status',  food_connection_data
        )
    


    
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
            defaults={'items': items},  # Store items as needed
            status=status
        ) 
        
        # Create Order instance
        order = Order.objects.create(
            sender=connection.buyer,
            receiver=connection.restaurant,
            status=status,
            location=connection.location,
            total_price=total_price,
            food_connection_id= connection.id
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
        print('Serializedfood item with id ',serialized)

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
                    # "image": item.food_menu.image,
                    "price": float(item.food_menu.price)  # Convert Decimal to float

                }
                order_items.append(item_data)

            # Add order details including item data
   
            orders_data.append({
                "id": order.id,
                "status": order.status,
                "location": order.location,
                "total_price": float(order.total_price),  # Convert Decimal to float
                "items": order_items,
                "order_id": order.order_id,
                "connection_id": order.food_connection_id
            })

        # Send back the detailed orders list to the client
        response_data = {
            'source': 'list.orders',
            'status': 'success', 
            "data":orders_data
        }

        # Send serialized data back to the client
        self.send(text_data=json.dumps(response_data))

        # self.send_group(
		# 	user, 'list.orders', response_data
		# )


    def  receive_food_list(self, data):
        user = self.scope['user']
        print("user",user)
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
        




    
    