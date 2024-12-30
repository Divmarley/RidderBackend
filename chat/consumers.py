import base64
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import  ContentFile
from django.db.models import Q, Exists, OuterRef
from django.db.models.functions import Coalesce

from accounts.models import CustomUser, VehicleInfo
from food.models import FoodMenu, Order, OrderItem, Restuarant
from food.serializers import FoodMenuSerializer, OrderSerializer
from ride.models import DriverHistory, RideHistory, TripHistory

from .models import Connection, DriverOnline, Message

from .serializers import (
	TripHistorySerializer,
	TripSerializer,
	UserSerializer, 
	SearchSerializer, 
	RequestSerializer, 
	FriendSerializer,
	MessageSerializer
)



class ChatConsumer(WebsocketConsumer):

	def connect(self):
		user = self.scope['user']
		print("user", user)


		if not user.is_authenticated:
			return
		# Save phone to use as a group name for this user
		self.phone = user.phone
		# Join this user to a group with their phone
		async_to_sync(self.channel_layer.group_add)(
			self.phone, self.channel_name
		)
		self.accept()

	def disconnect(self, close_code):
		# Leave room/group
		async_to_sync(self.channel_layer.group_discard)(
			self.phone, self.channel_name
		)

	#-----------------------
	#    Handle requests
	#-----------------------

	def receive(self, text_data):
		# Receive message from websocket
		data = json.loads(text_data)
		# Log incoming message


		print('Received message:', json.dumps(data, indent=2))
		
		data_source = data.get('source') 

		print('data_source:',data_source)
		
		# Pretty print  python dict
		print('receive', json.dumps(data, indent=2))
		# Get friend list
		if data_source == 'trip.lookForDriver':
			self.receive_trip_lookForDriver(data)

		# Get friend list
		if data_source == 'friend.list':
			self.receive_friend_list(data)

		# Message List
		elif data_source == 'message.list':
			self.receive_message_list(data)

		# Message has been sent
		elif data_source == 'message.send':
			self.receive_message_send(data)

		# User is typing message
		elif data_source == 'message.type':
			self.receive_message_type(data)

		# Accept friend request
		elif data_source == 'request.accept':
			print("request.accept",)
			self.receive_request_accept(data)

		# Make friend request
		elif data_source == 'request.connect':
			self.receive_request_connect(data)

		# Get request list
		elif data_source == 'request.list':
			self.receive_request_list(data)

		# Search / filter users
		elif data_source == 'search':
			self.receive_search(data)

		# Thumbnail upload
		elif data_source == 'thumbnail':
			self.receive_thumbnail(data)

		elif data_source == 'create.food.order':
			print('hello')
			self.receive_order_create(data)

		elif data_source == 'order.list':
			self.receive_order_list(data)

		elif data_source == 'order.accept':
			self.receive_order_accept(data)

		elif data_source == 'order.decline':
			self.receive_order_decline(data)

		elif data_source == 'driver.accepted':
			self.receive_start_trip(data)
		
		elif data_source == 'driver.arrived':
			self.receive_driver_arrived(data)

		elif data_source == 'trip.start':
			self.receive_start_trip(data)

		elif data_source == 'trip.ended':
			self.receive_trip_ended(data)

		elif data_source == 'trip.done':
			self.receive_trip_done(data)

		elif data_source == 'trip.rating':
			self.receive_rating(data)


		elif data_source == 'foodOrder.create':
			self.receive_food_order_create(data)
		
		elif data_source == 'confirm.payment':
			self.receive_trip_confirm_payment(data)

		elif data_source == 'driver.location':
			self.receive_locationUpdate(data)

		elif data_source == 'user.update':
			self.receive_userUpdate(data)


	# def receive_food_order_create(self, data):
	# 	user = self.scope['user']
	# 	restaurant_id = data.get('restaurant_id')
	# 	food_items = data.get('food_items')

	# 	# Assuming you have a model for FoodOrder and serializer defined
	# 	# Replace with your actual models and serializers
	# 	food_order = Order.objects.create(
	# 		user=user,
	# 		restaurant_id=restaurant_id,
	# 		food_items=food_items
	# 	)

	# 	serialized_order = OrderSerializer(food_order).data
	# 	self.send_group(user.phone, 'foodOrder.create', serialized_order)

	# 	self.send_group('552297798', 'foodOrder.create', serialized_order)

	# def receive_order_create(self, data):
	
	# 	user = self.scope['user']
	# 	print(user)
	# 	order_data = data.get('order')

	# 	print("order",order_data)
	# 	# order_number = data.get('order_number')
	# 	# order_number = data.get('order_number')
	# 	# description = data.get('description')

	# 	receiverInstance = Restaurant.objects.get(user=order_data['restaurant'])
 

	# 	order = Order.objects.create(
	# 		sender=user,
	# 		status=order_data['status'],
	# 		# items=order['items'],
	# 		total_price=order_data['total_price'],
	# 		location=order_data['location'],
	# 		receiver= receiverInstance
	# 	)

	# 	# Assuming `order_data` is the original dictionary containing the order information, including items
	# 	for item in order_data['items']:
	# 		print(item)
	# 		food_menu_item = FoodMenu.objects.get(id=item['item_id'])  # Fetch FoodMenu object using 'item_id'
	# 		OrderItem.objects.create(
	# 			order=order,  # This is the created Order object
	# 			item=food_menu_item,
	# 			quantity=item['quantity']
	# 		)


	# 	print("order",order)
	# 	print("food_menu_item",food_menu_item)

	# 	serialized_order = OrderSerializer(order)
	# 	serialized_food = FoodMenuSerializer(food_menu_item)

	# 	print("serialized_food",serialized_food.data) 
	# 	self.send_group(user.phone, 'create.food.order', serialized_order.data) 
	# 	# self.send_group(order['restaurant'], 'create.food.order', serialized_order.data)
	def receive_order_create(self, data):
		user = self.scope['user']
		 
		order_data = data.get('order')

		# print("order", order_data)
		print("dataapp", data)

		# Get the receiver instance
		receiver_instance = Restuarant.objects.get(user=order_data['restaurant'])

		# Create the Order instance
		order = Order.objects.create(
			sender=user,
			status=order_data['status'],
			total_price=order_data['total_price'],
			location=order_data['location'],
			receiver=receiver_instance
		)

		serialized_food_items = []

		# Loop through the items in the order and create OrderItem instances
		for item in order_data['items']:
			print(item)
			food_menu_item = FoodMenu.objects.get(id=item['item_id'])  # Fetch FoodMenu object using 'item_id'
			order_item = OrderItem.objects.create(
				order=order,
				item=food_menu_item,
				quantity=item['quantity']
			)
			
			# Serialize the food item and add to the list
			serialized_food = FoodMenuSerializer(food_menu_item).data
			serialized_food_items.append(serialized_food)

		# Serialize the order
		serialized_order = OrderSerializer(order)

		# Print the serialized food items
		print("serialized_food_items", serialized_food_items)

		# Send serialized order data along with serialized food items
		response_data = {
			'order': serialized_order.data,
			'food_items': serialized_food_items,
			"data": data
		}

		self.send_group(user.phone, 'create.food.order', response_data)

	def receive_order_list(self, data):
		user = self.scope['user']
		if not user:
			self.send(text_data=json.dumps({
				'error': 'User is not authenticated'
			}))
			return

		try:
			orders = Order.objects.filter(receiver=user)
			serialized_orders = OrderSerializer(orders, many=True)
			print('serialized_orders',serialized_orders)
			self.send(text_data=json.dumps({
				'type': 'order.list',
				'orders': serialized_orders.data
			}))
		except Exception as e:
			self.send(text_data=json.dumps({
				'error': str(e)
			}))

	def receive_order_accept(self, data):
		order_id = data.get('order_id')
		try:
			order = Order.objects.get(id=order_id)
		except Order.DoesNotExist:
			return

		order.status = 'accepted'
		order.save()

		serialized_order = OrderSerializer(order)
		self.send_group(order.sender.phone, 'order.accept', serialized_order.data)
		self.send_group(
			order.receiver.phone, 'request.accept', serialized_order.data
		)

	def receive_order_decline(self, data):
		order_id = data.get('order_id')
		try:
			order = Order.objects.get(id=order_id)
		except Order.DoesNotExist:
			return

		order.status = 'declined'
		order.save()

		serialized_order = OrderSerializer(order)
		self.send_group(order.user.phone, 'order.decline', serialized_order.data)
	
	def receive_trip_lookForDriver(self,data):
		user = self.scope['user']
		print('received', data)
		self.send_group(user.phone, 'trip.lookForDriver', data)

	def receive_friend_list(self, data):
		user = self.scope['user']
		# Latest message subquery
		latest_message = Message.objects.filter(
			connection=OuterRef('id')
		).order_by('-created')[:1]
		# print("latest_message",latest_message)
		# Get connections for user
		connections = Connection.objects.filter(
			Q(sender=user) | Q(receiver=user),
			accepted=True
		).annotate(
			latest_text   =latest_message.values('text'),
			latest_created=latest_message.values('created')
		).order_by(
			Coalesce('latest_created', 'updated').desc()
		)
		serialized = FriendSerializer(
			connections, 
			context={ 
				'user': user
			}, 
			many=True)
		# Send data back to requesting user
		self.send_group(user.phone, 'friend.list', serialized.data)

	def receive_message_list(self, data):
		user = self.scope['user']
		connectionId = data.get('connectionId')
		page = data.get('page')
		page_size = 15
		try:
			connection = Connection.objects.get(id=connectionId)
		except Connection.DoesNotExist:
			print('Error: couldnt find connection')
			return
		# Get messages
		messages = Message.objects.filter(
			connection=connection
		).order_by('-created')[page * page_size:(page + 1) * page_size]
		# Serialized message
		serialized_messages = MessageSerializer(
			messages,
			context={ 
				'user': user 
			}, 
			many=True
		)
		# Get recipient friend
		recipient = connection.sender
		if connection.sender == user:
			recipient = connection.receiver
		
		# Serialize friend
		serialized_friend = UserSerializer(recipient)

		# Count the total number of messages for this connection
		messages_count = Message.objects.filter(
			connection=connection
		).count()

		next_page = page + 1 if messages_count > (page + 1 ) * page_size else None

		data = {
			'messages': serialized_messages.data,
			'next': next_page,
			'friend': serialized_friend.data
		}
		# Send back to the requestor
		self.send_group(user.phone, 'message.list', data)

	def receive_message_send(self, data):
		user = self.scope['user']
		connectionId = data.get('connectionId')
		print(connectionId)
		message_text = data.get('message')
		try:
			connection = Connection.objects.get(id=connectionId)
		except Connection.DoesNotExist:
			print('Error: couldnt find connection')
			return
		
		message = Message.objects.create(
			connection=connection,
			user=user,
			text=message_text
		)

		# Get recipient friend
		recipient = connection.sender
		if connection.sender == user:
			recipient = connection.receiver

		# Send new message back to sender
		serialized_message = MessageSerializer(
			message,
			context={
				'user': user
			}
		)
		serialized_friend = UserSerializer(recipient)
		data = {
			'message': serialized_message.data,
			'friend': serialized_friend.data
		}
		self.send_group(user.phone, 'message.send', data)

		# Send new message to receiver
		serialized_message = MessageSerializer(
			message,
			context={
				'user': recipient
			}
		)
		serialized_friend = UserSerializer(user)
		data = {
			'message': serialized_message.data,
			'friend': serialized_friend.data
		}
		self.send_group(recipient.phone, 'message.send', data)

	def receive_message_type(self, data):
		user = self.scope['user']
		recipient_phone = data.get('phone')
		data = {
			'phone': user.phone
		}
		self.send_group(recipient_phone, 'message.type', data)

	def receive_request_accept(self, data):
		print('received', data)
		phone = data.get('phone')
		dataDriver = data.get('dataDriver')
		
		try:
			# Fetch connection object
			connection = Connection.objects.get(
				sender__phone=phone,
				receiver=self.scope['user']
			)
		except Connection.DoesNotExist:
			print('Error: connection does not exist')
			return
		
		# Fetch driver's vehicle information
		try:
			vehicle_info = VehicleInfo.objects.get(driver=self.scope['user'])
			vehicle_data = {
				"vehicle_name": vehicle_info.vehicle_name,
				"model": vehicle_info.model,
				"color": vehicle_info.color,
				"year": vehicle_info.year,
				"vehicle_registration_number": vehicle_info.vehicle_registration_number,
				"vehicle_license_number": vehicle_info.vehicle_license_number,
			}
		except VehicleInfo.DoesNotExist:
			vehicle_data = None  # No vehicle info available

		# Update the connection
		connection.accepted = True
		connection.status = "DRIVER ACCEPTED"
		connection.data_driver = dataDriver
		connection.save()
		
		serialized = RequestSerializer(connection)
		print("RequestSerializer", serialized.data)
		
		# Include vehicle data in serialized data
		serialized_data = serialized.data
		serialized_data["vehicle_info"] = vehicle_data

		# Send accepted request to sender
		self.send_group(
			connection.sender.phone, 'request.accept', serialized_data
		)

		# Send accepted request to receiver
		self.send_group(
			connection.receiver.phone, 'request.accept', serialized_data
		)

		# Send new friend object to sender
		serialized_friend = FriendSerializer(
			connection,
			context={
				'user': connection.sender,
				'dataDriver': connection.data_driver
			}
		)
		self.send_group(
			connection.sender.phone, 'friend.new', serialized_friend.data)

		# Send new friend object to receiver
		serialized_friend = FriendSerializer(
			connection,
			context={
				'user': connection.receiver,
				'driverTripData': connection.data_driver
			}
		)
		self.send_group(
			connection.receiver.phone, 'friend.new', serialized_friend.data)

	def receive_request_connect(self, data):
		phone = data.get('phone')
		location = data.get('location')
		push_token = data.get('push_token')
		riderPushToken = data.get('riderPushToken')

		print("receive_request_connect data",data)
		# Attempt to fetch the receiving user
		try:
			receiver = CustomUser.objects.get(phone=phone)
		except CustomUser.DoesNotExist:
			print('Error: User not found')
			return
		# Create connection
		connection, _ = Connection.objects.get_or_create(
			sender=self.scope['user'],
			receiver=receiver,
			location=location,
			pushToken= push_token,
			riderPushToken= riderPushToken,
			status='LOOKING FOR DRIVER'
 
		)
		
		# Serialized connection
		serialized = RequestSerializer(connection)
		# Send back to sender
		self.send_group(
			connection.sender.phone, 'request.connect', serialized.data
		)
		# Send to receiver
		self.send_group(
			connection.receiver.phone, 'request.connect', serialized.data
		)

	def receive_request_list(self, data):
		user = self.scope['user']
		# Get connection made to this  user
		connections = Connection.objects.filter(
			receiver=user,
			accepted=False
		)
		serialized = RequestSerializer(connections, many=True)
		# Send requests lit back to this userr
		self.send_group(user.phone, 'request.list', serialized.data)
	
	def receive_search(self, data):
		query = data.get('query')
		# Get users from query search term
		users = CustomUser.objects.filter(
			Q(phone__istartswith=query)   |
			Q(first_name__istartswith=query) |
			Q(last_name__istartswith=query)
		).exclude(
			phone=self.phone
		).annotate(
			pending_them=Exists(
				Connection.objects.filter(
					sender=self.scope['user'],
					receiver=OuterRef('id'),
					accepted=False
				)
			),
			pending_me=Exists(
				Connection.objects.filter(
					sender=OuterRef('id'),
					receiver=self.scope['user'],
					accepted=False
				)
			),
			connected=Exists(
				Connection.objects.filter(
					Q(sender=self.scope['user'], receiver=OuterRef('id')) |
					Q(receiver=self.scope['user'], sender=OuterRef('id')),
					accepted=True
				)
			)
		)
		# serialize results
		serialized = SearchSerializer(users, many=True)
		# Send search results back to this user
		self.send_group(self.phone, 'search', serialized.data)
  
	def receive_thumbnail(self, data):
		user = self.scope['user']
		# Convert base64 data  to django content file
		image_str = data.get('base64')
		print(image_str)
		image = ContentFile(base64.b64decode(image_str))
		# Update thumbnail field
		filename = data.get('filename')
		user.thumbnail.save(filename, image, save=True)
		# Serialize user
		serialized = UserSerializer(user)
		# Send updated user data including new thumbnail 
		self.send_group(self.phone, 'thumbnail', serialized.data)

	def receive_driver_arrived(self, data):
		print('receive_driver_arrived-.....> ',data)   
		phone = data.get('phone') 
		# Fetch connection object
		try:
			connection = Connection.objects.get(
				sender__phone=phone,
				receiver=self.scope['user']
			)
			
		except Connection.DoesNotExist:
			print('Error: connection  doesnt exists')
			return
		# Update the connection
		connection.status = 'DRIVER ARRIVED'
		connection.save()
		
		serialized = TripSerializer(connection)
		print("serialized.data",serialized.data)

		# Send accepted request to sender
		self.send_group(
			connection.sender.phone, 'driver.arrived', serialized.data
		)
		# Send accepted request to receiver
		self.send_group(
			connection.receiver.phone, 'driver.arrived', serialized.data
		)

	def receive_start_trip(self, data): 
		phone = data.get('phone')
	 
		# Fetch connection object
		try:
			connection = Connection.objects.get(
				sender__phone=phone,
				receiver=self.scope['user']
			)
			
		except Connection.DoesNotExist:
			print('Error: connection  doesnt exists')
			return
		# Update the connection
		connection.status = 'TRIP STARTED'
		connection.save()
		
		serialized = TripSerializer(connection)

		# Send accepted request to sender
		self.send_group(
			connection.sender.phone, 'trip.start', serialized.data
		)
		# Send accepted request to receiver
		self.send_group(
			connection.receiver.phone, 'trip.start', serialized.data
		)

	def receive_trip_ended(self, data): 
		print("data: ",	data)
		phone = data.get('phone')
		# Fetch connection object
		print("user",self.scope['user'])
		try:
			connection = Connection.objects.get(
				sender__phone=phone,
				receiver=self.scope['user']
			)
			
		except Connection.DoesNotExist:
			print('Error: connection  doesnt exists')
			return
		# Update the connection
		connection.status = 'TRIP ENDED'
		connection.paymentStatus = 1
		connection.save() 
		TripHistory.objects.create(
			rider=connection.sender.id,
			driver=connection.receiver.id,
			status=1,
			destination=connection.location,
			paymentStatus=connection.paymentStatus,
			paymentType='CASH',
			paymentAmount=connection.location['estimatedPrice'],
			paidAmount=connection.location['estimatedPrice']
			)
		# RideHistory.objects.create(user=connection.sender.id,destination=connection.location,date=connection.updated,paymentStatus=connection.status,amount=100)
		# DriverHistory.objects.create(driver=connection.receiver.id,destination=connection.location,date=connection.updated,paymentStatus=connection.status,amount=100)
		# connection.delete()
		serialized = TripSerializer(connection)

		# Send accepted request to sender
		self.send_group(
			connection.sender.phone, 'trip.ended', serialized.data
		)
		# Send accepted request to receiver
		self.send_group(
			connection.receiver.phone, 'trip.ended', serialized.data
		)


	def receive_trip_done(self, data): 
		print("data: ",	data)
 
		# Fetch connection object
		print("user",self.scope['user'])
		try:
			connection = Connection.objects.get(
				sender__phone=self.scope['user'],
			
			)
			print("connection",connection)
			
		except Connection.DoesNotExist:
			print('Error: connection  doesnt exists')
			return
		# Update the connection
		connection.status = 'RATING'
		connection.paymentStatus = 1
		connection.save() 
		# TripHistory.objects.create(
		# 	rider=connection.sender.id,
		# 	driver=connection.receiver.id,
		# 	status=1,
		# 	destination=connection.location,
		# 	paymentStatus=connection.paymentStatus,
		# 	paymentType='CASH',
		# 	paymentAmount=connection.location['estimatedPrice'],
		# 	paidAmount=connection.location['estimatedPrice']
		# 	)
		# RideHistory.objects.create(user=connection.sender.id,destination=connection.location,date=connection.updated,paymentStatus=connection.status,amount=100)
		# DriverHistory.objects.create(driver=connection.receiver.id,destination=connection.location,date=connection.updated,paymentStatus=connection.status,amount=100)
		# connection.delete()
		serialized = TripSerializer(connection)

		# Send accepted request to sender
		self.send_group(
			connection.sender.phone, 'trip.done', serialized.data
		)
		# Send accepted request to receiver
		self.send_group(
			connection.receiver.phone, 'trip.done', serialized.data
		)


	def receive_rating(self, data): 
		print("data: ",	data)
 
		# Fetch connection object
		print("user",self.scope['user'])
		try:
			connection = Connection.objects.get(
				sender__phone=self.scope['user'],
			
			)
			print("connection",connection)
			
		except Connection.DoesNotExist:
			print('Error: connection  doesnt exists')
			return
		# Update the connection
		connection.status = 'IDEL'
		connection.paymentStatus = 1
		# connection.delete() 
		TripHistory.objects.create(
			rider=connection.sender.id,
			driver=connection.receiver.id,
			status=1,
			destination=connection.location,
			paymentStatus=connection.paymentStatus,
			paymentType='CASH',
			paymentAmount=connection.location['estimatedPrice'],
			paidAmount=connection.location['estimatedPrice']
			)
		# RideHistory.objects.create(user=connection.sender.id,destination=connection.location,date=connection.updated,paymentStatus=connection.status,amount=100)
		# DriverHistory.objects.create(driver=connection.receiver.id,destination=connection.location,date=connection.updated,paymentStatus=connection.status,amount=100)
		connection.delete()
		serialized = TripSerializer(connection)

		# Send accepted request to sender
		self.send_group(
			connection.sender.phone, 'trip.rating', serialized.data
		)
		# Send accepted request to receiver
		self.send_group(
			connection.receiver.phone, 'trip.rating', serialized.data
		)


	def receive_trip_confirm_payment(self, data): 
		print("data: ",	data)
		phone = data.get('phone')
		# Fetch connection object
		
		try:
			connection = Connection.objects.get(
				sender__phone=phone,
				receiver=self.scope['user']
			)
			print("connection",connection)
		except Connection.DoesNotExist:
			print('Error: connection  doesnt exists',)
			return
		# Update the connection
		connection.status = 'PAYMENT CONFIRM'
		connection.paymentStatus = 1
		 
		connection.save()
		# TripHistory.objects.create(
		# 	rider=connection.sender.id,
		# 	driver=connection.receiver.id,
		# 	status=1,
		# 	destination=connection.location,
		# 	paymentStatus=connection.paymentStatus,
		# 	paymentType='CASH',
		# 	paymentAmount=20,
		# 	paidAmount=20
		# 	)
		 
		# RideHistory.objects.create(user=connection.sender.id,destination=connection.location,date=connection.updated,paymentStatus=connection.status, paymentAmount=20,amount=100)
		# DriverHistory.objects.create(driver=connection.receiver.id,destination=connection.location,date=connection.updated,paymentStatus=connection.status,paymentAmount=20,amount=100)
		# connection.delete()
		serialized = TripSerializer(connection)
		
		# Send accepted request to sender
		self.send_group(
			connection.sender.phone, 'confirm.payment', serialized.data
		)
		# Send accepted request to receiver
		self.send_group(
			connection.receiver.phone, 'confirm.payment', serialized.data
		)

	def receive_locationUpdate(self, data):
		try:
			# Log the incoming location data
			print('Receiving location update:', data)

			# Extract the necessary fields from the incoming data
		 
			latitude = data['data']['latitude']
			longitude = data['data']['longitude']
			# Ensure all required data is present
			if  latitude is None or longitude is None:
				print('Invalid data received: missing fields')
				return
			
			# Update the driver's location in the database
			try:
				# Assuming you have a Driver model and 'driver_id' is valid
				# driver = DriverHistory.objects.get(id=driver_id)
				# driver.latitude = latitude
				# driver.longitude = longitude
				# driver.save()

				# Log the update
				# print(f"Updated location for driver {driver_id}: ({latitude}, {longitude})")
				user = self.scope['user']
				connection = Connection.objects.filter(
					sender__phone=user.phone, accepted=True
				).first()
				# Optionally, broadcast the location update to a group (e.g., for tracking in real-time)
				self.send_group(user.phone, 'driver.locationUpdate', {
					'user_id': user.id,
					'latitude': latitude,
					'longitude': longitude
				})
    
				self.send_group(connection.receiver.phone, 'driver.locationUpdate', {
					'driver_id': connection.receiver.id,
					'latitude': latitude,
					'longitude': longitude
				})
    
			except DriverHistory.DoesNotExist:
				print(f"Driver with ID {connection.receiver.id} does not exist")

		except Exception as e:
			print(f"Error in location update: {str(e)}")
 
	def receive_userUpdate(self, data):
		# Get the currently authenticated user
		user = self.scope['user']
		
		# Log the received data for debugging
		print("Received user update", data, user)
		
		# Extract the user object from the incoming data
		updated_user_data = data.get('user')
		
		if updated_user_data:
			# Get the new name and phone from the nested user object, or fallback to current values
			new_name = updated_user_data.get('name') or user.phone  # Use phone as fallback for name
			new_phone = updated_user_data.get('phone') or user.phone  # Use current phone if not provided
			new_email = updated_user_data.get('email') or user.phone  # Use current phone if not provided

			# Update the user's name and phone
			if new_name:
				user.name = new_name
			if new_phone:
				user.phone = new_phone
			if new_email:
				user.email = new_email
			
			# Save the updated user
			user.save()
			
			# Serialize the updated user
			serialized = UserSerializer(user)
			
			# Send the updated user data back to the group, including the new name and phone
			self.send_group(self.phone, 'user.update', serialized.data)

	def receive_online_drivers(self, data):
		# Get all online drivers
		online_drivers = DriverOnline.objects.filter(is_online=True).select_related('driver')
		
		# Prepare response data
		drivers_data = []
		for driver in online_drivers:
			drivers_data.append({
				'driver_id': driver.driver.id,
				'name': driver.driver.get_full_name(),
				'phone': driver.phone,
				'location': driver.location,
				'latitude': driver.latitude,
				'longitude': driver.longitude,
				'vehicle': {
					'name': driver.driver.vehicle_name,
					'model': driver.driver.model,
					'color': driver.driver.color,
					'registration': driver.driver.vehicle_registration_number
				}
			})

		# Send response through WebSocket
		self.send_group(self.scope['user'].phone, 'drivers.online', {
			'online_drivers': drivers_data
		})

	#--------------------------------------------
	#   Catch/all broadcast to client helpers
	#--------------------------------------------

	def send_group(self, group, source, data):
		response = {
			'type': 'broadcast_group',
			'source': source,
			'data': data
		}
		async_to_sync(self.channel_layer.group_send)(
			group, response
		)

	def broadcast_group(self, event):
		'''
		event:
			- type: 'broadcast_group'
			- source: where it originated from
			- data: whatever you want to send as a dict
		'''
		# Send only the source and data to the client
		self.send(text_data=json.dumps({
			'source': event['source'],
			'data': event['data']
		}))
		


