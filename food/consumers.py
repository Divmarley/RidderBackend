from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from accounts.models import CustomUser
import json
from asgiref.sync import async_to_sync
from food.models import FoodConnection,Restaurant
from food.serializers import RequestFoodSerializer



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
        
    
    def receive_food_request_connect(self, data):
        print("receive_food_request_connect", data.get('data'))
        daseData = data.get('data')

        location = daseData['location']
        phone = daseData['phone']
        restaurant = daseData['restaurant']
        pushToken = daseData['pushToken']
        items = daseData['items']
        user = self.scope['user']
        print("user",user)
        if not user:
            self.send(text_data=json.dumps({
                'error': 'User is not authenticated'
            }))
            return
 
		# Attempt to fetch the receiving user
        try:
            restaurant = CustomUser.objects.get(id=restaurant)
            print('restaurant',restaurant)
        except CustomUser.DoesNotExist:
            print('Error: User not found')
            return
		# Create connection
        connection, _ = FoodConnection.objects.get_or_create(
			buyer=self.scope['user'],
            restaurant= restaurant,
			location=location,
			pushToken=pushToken,
            items=items
		)

        print("connection",connection)

        print('Received food request',) 
        
        # # Serialized connection
        serialized = RequestFoodSerializer(connection)
   
        # # Send back to sender
        self.send_group(
            connection.buyer.phone, 'request.connect.food', serialized.data
        )
        # # Send to receiver
        self.send_group(
            connection.restaurant.phone, 'request.connect.food', serialized.data
		)


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
        




    
    