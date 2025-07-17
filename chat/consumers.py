import base64
import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import  ContentFile
from django.db.models import Q, Exists, OuterRef
from django.db.models.functions import Coalesce

from accounts.models import CustomUser, VehicleInfo
from food.models import FoodMenu, Order, OrderItem, Restaurant
from food.serializers import FoodMenuSerializer, OrderSerializer
from ride.models import DriverHistory, RideHistory, TripHistory

from .models import Connection, DriverOnline, Message

from .serializers import (
	DriverOnlineSerializer,
	TripHistorySerializer,
	TripSerializer,
	UserSerializer, 
	SearchSerializer, 
	RequestSerializer, 
	FriendSerializer,
	MessageSerializer
)

logger = logging.getLogger(__name__)

class ChatConsumer(WebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.phone = None
		self.user = None
		self.group_name = None

	def connect(self):
		try:
			# Get user from scope
			self.user = self.scope['user']
			logger.info(f"Connection attempt from user: {self.user}")

			if not self.user.is_authenticated:
				logger.warning("Unauthenticated connection attempt")
				self.close()
				return

			# Set phone attribute
			self.phone = getattr(self.user, 'phone', None)
			if not self.phone:
				logger.error("User has no phone number")
				self.close()
				return

			# Join user's group
			self.group_name = str(self.phone)
			async_to_sync(self.channel_layer.group_add)(
				self.group_name,
				self.channel_name
			)
			self.accept()
			logger.info(f"Successfully connected user {self.phone}")

		except Exception as e:
			logger.error(f"Connection error: {str(e)}")
			self.close()

	def disconnect(self, close_code):
		try:
			if hasattr(self, 'group_name') and self.group_name:
				async_to_sync(self.channel_layer.group_discard)(
					self.group_name,
					self.channel_name
				)
				logger.info(f"Disconnected user from group {self.group_name}")
		except Exception as e:
			logger.error(f"Disconnect error: {str(e)}")

	def receive(self, text_data):
		# try:
		# 	if not self.user or not self.user.is_authenticated:
		# 		return
			
		data = json.loads(text_data)
		data_source = data.get('source')

		# Pretty print  python dict
		print('receive', json.dumps(data, indent=2))

		if data_source == 'trip.lookForDriver':
			self.receive_trip_lookForDriver(data)
		elif data_source == 'friend.list':
			self.receive_friend_list(data)
		elif data_source == 'message.list':
			self.receive_message_list(data)
		elif data_source == 'message.send':
			self.receive_message_send(data)
		elif data_source == 'message.type':
			self.receive_message_type(data)
		elif data_source == 'request.accept':
			self.receive_request_accept(data)
		elif data_source == 'request.connect':
			self.receive_request_connect(data)
		elif data_source == 'request.list':
			self.receive_request_list(data)
		elif data_source == 'search':
			self.receive_search(data)
		elif data_source == 'thumbnail':
			self.receive_thumbnail(data)
		elif data_source == 'create.food.order':
			logger.debug('hello')
			self.receive_order_create(data)
		elif data_source == 'order.list':
			self.receive_order_list(data)
		elif data_source == 'order.accept':
			self.receive_order_accept(data)
		elif data_source == 'order.decline':
			self.receive_order_decline(data)
		# elif data_source == 'driver.accepted':
		# 	self.receive_start_trip(data)
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
		elif data_source == 'request.cancel':
			self.receive_request_cancel(data)
		elif data_source == 'location.rider.update':
			self.receive_rider_location_update(data)
			# location.driver.update
		elif data_source == 'location.driver.update':
			self.receive_driver_location_update(data)
		elif data_source == 'drivers.online':
			self.receive_online_drivers(data)
		elif data_source == 'driver.online':
			self.receive_online_driver_data(data)

		# except Exception as e:
		# 	logger.error(f"Error processing message: {str(e)}")

	def receive_order_create(self, data):
		user = self.scope['user']
		 
		order_data = data.get('order')


		# Get the receiver instance
		receiver_instance = Restaurant.objects.get(user=order_data['restaurant'])

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
		self.send_group(user.phone, 'trip.lookForDriver', data)

	def receive_friend_list(self, data):
		user = self.scope['user']
		# Latest message subquery
		latest_message = Message.objects.filter(
			connection=OuterRef('id')
		).order_by('-created')[:1]
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
		phone = data.get('phone')
		dataDriver = data.get('dataDriver')
		connectionId = data.get('connectionId')
		pushToken = data.get('pushToken')
		
		print('receive_request_accept dataDriver,',dataDriver)
		# print('receive_request_accept riderPushToken,',push_token)
		# print('receive_request_accept data,',data)
		
		try:
			# Fetch connection object
			connection = Connection.objects.get(
				sender__phone=phone,
				receiver=self.scope['user'],
				id=connectionId
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
		connection.pushToken = 'ffefe'
		connection.save()

		# Delete other pending connections for this driver
		other_connections = Connection.objects.filter(
			sender=connection.sender_id,
			accepted=False
		).exclude(id=connectionId)


		# Notify other riders about cancellation before deleting
		for other_conn in other_connections:
			cancel_data = {
				'id': other_conn.id,
				'status': 'cancelled',
				'reason': 'Driver accepted another request'
			}
			self.send_group(
				other_conn.sender.phone, 
				'request.cancel', 
				cancel_data
			)
		
		# Delete other connections
		other_connections.delete()
		
		serialized = RequestSerializer(connection)
		
		# Include vehicle data in serialized data
		serialized_data = serialized.data
		serialized_data["vehicle_info"] = vehicle_data

		# Send accepted request to sender
		self.send_group(
			connection.sender.phone, 
			'request.accept', 
			serialized_data
		)

		# Send accepted request to receiver
		self.send_group(
			connection.receiver.phone, 
			'request.accept', 
			serialized_data
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
			connection.sender.phone, 
			'friend.new', 
			serialized_friend.data
		)

		# Send new friend object to receiver
		serialized_friend = FriendSerializer(
			connection,
			context={
				'user': connection.receiver,
				'driverTripData': connection.data_driver
			}
		)
		self.send_group(
			connection.receiver.phone, 
			'friend.new', 
			serialized_friend.data
		)

	def receive_request_connect(self, data):
		phone = data.get('phone')
		location = data.get('location')
		push_token = data.get('push_token')
		riderPushToken = data.get('riderPushToken')
  
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
		image = ContentFile(base64.b64decode(image_str))
		# Update thumbnail field
		filename = data.get('filename')
		user.thumbnail.save(filename, image, save=True)
		# Serialize user
		serialized = UserSerializer(user)
		# Send updated user data including new thumbnail 
		self.send_group(self.phone, 'thumbnail', serialized.data)

	def receive_driver_arrived(self, data):
		phone = data.get('phone') 
		connectionId = data.get('connectionId') 
		# Fetch connection object
		try:
			connection = Connection.objects.get(
				sender__phone=phone,
				receiver=self.scope['user'],
				id=connectionId
			)
			
		except Connection.DoesNotExist:
			print('Error: connection  doesnt exists')
			return
		# Update the connection
		connection.status = 'DRIVER ARRIVED'
		connection.save()
		
		serialized = TripSerializer(connection)

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
		connectionId = data.get('connectionId')
	 
		# Fetch connection object
		try:
			connection = Connection.objects.get(
				receiver__phone=phone,
				receiver=self.scope['user'],
				id=connectionId
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
		phone = data.get('phone')
		connectionId = data.get('connectionId')
		# Fetch connection object
		try:
			connection = Connection.objects.get(
				receiver__phone=phone,
				receiver=self.scope['user'],
				id=connectionId
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
 
		# Fetch connection object
		try:
			connection = Connection.objects.get(
				sender__phone=self.scope['user'],
		 
			
			)
 
			
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
 
		# Fetch connection object
		try:
			connection = Connection.objects.get(
				sender__phone=self.scope['user'],
			
			)
			
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
			paidAmount=connection.location['estimatedPrice'],
			pickupPoint=connection.location['pickupPoint']
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
		phone = data.get('phone')
		connectionId = data.get('connectionId')
		# Fetch connection object
		
		try:
			connection = Connection.objects.get(
				receiver__phone=phone,
				receiver=self.scope['user'],
				id= connectionId
			)
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

			# Extract the necessary fields from the incoming data
		 
			latitude = data['data']['latitude']
			longitude = data['data']['longitude']
			# Ensure all required data is present
			if  latitude is None or longitude is None:
				return
			
			# Update the driver's location in the database
			try:
				# Assuming you have a Driver model and 'driver_id' is valid
				# driver = DriverHistory.objects.get(id=driver_id)
				# driver.latitude = latitude
				# driver.longitude = longitude
				# driver.save()

				# Log the update
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
		"""Handles user profile updates received via WebSocket"""
		
		# Get the currently authenticated user
		user = self.scope['user']

		# Log received data for debugging
		print("🔹 Received user update:", data)

		# Extract user data from the request
		updated_user_data = data.get('user', {})

		# Ensure at least one field is provided
		if not updated_user_data:
			self.send(text_data=json.dumps({'error': 'No update data provided'}))
			return

		# Extract new values or fallback to current values
		new_name = updated_user_data.get('name', user.name)
		new_phone = updated_user_data.get('phone', user.phone)
		new_email = updated_user_data.get('email', user.email)

		# Only update fields that have changed
		fields_to_update = {}
		if new_name and new_name != user.name:
			fields_to_update['name'] = new_name
		if new_phone and new_phone != user.phone:
			fields_to_update['phone'] = new_phone
		if new_email and new_email != user.email:
			fields_to_update['email'] = new_email

		if fields_to_update:
			for field, value in fields_to_update.items():
				setattr(user, field, value)
			user.save()
			print(f"✅ User updated successfully: {fields_to_update}")

			# Serialize and send the updated user data
			serialized = UserSerializer(user)
			self.send_group(user.phone, 'user.update', serialized.data)
		else:
			print("ℹ️ No changes detected, skipping update")

	def receive_online_driver_data(self, data):
		user = self.scope['user']
		online_drivers = DriverOnline.objects.get(driver=user)
		# print('online_drivers',online_drivers)

		serialized = DriverOnlineSerializer(online_drivers)
		# print('serialized',serialized.data)
		self.send_group(user.phone, 'driver.online', serialized.data)

 
	def receive_online_drivers(self, data):
		# Get all online drivers
		ride_type = data.get('data', {}).get('ride_type')
		 
		
		# Filter online drivers by ride type if specified
		query = Q(is_online=True)
		if ride_type:
			query &= Q(ride_type==ride_type)
			
		online_drivers = DriverOnline.objects.filter(is_online=True,ride_type=ride_type).select_related('driver')
		# connection  doesnt exists',online_drivers)
		# Prepare response data
		drivers_data = []
		for driver in online_drivers:
			drivers_data.append({
				'driver_id': driver.driver.id,
				'name': driver.driver.name,
				'phone': driver.phone,
				'location': driver.location,
				'latitude': driver.latitude,
				'longitude': driver.longitude,
				'ride_type': driver.ride_type
			})
 
		# Send response through WebSocket
		self.send_group(self.scope['user'].phone, 'drivers.online', {
			'online_drivers': drivers_data
		})

	def receive_rider_location_update(self, data):
		# print('Received location update', data)
		try:
			# Get the user and location data
			user = self.scope['user']
			# print('user.phone',user.phone)
			location_data = data.get('data')
			
			if not location_data:
				print('No location data received')
				return
				
			# Extract location details
			latitude = location_data.get('latitude')
			longitude = location_data.get('longitude')
			accuracy = location_data.get('accuracy')
			speed = location_data.get('speed')
			timestamp = location_data.get('timestamp')
			
			# Find active connection for the driver
			try:
				connection = Connection.objects.filter(
				 
					accepted=True,
					sender__phone=user.phone,
					# status__in=['DRIVER ACCEPTED', 'TRIP STARTED']
				).first()

				# connection = Connection.objects.filter(
				# 	sender__phone=user.phone,  
				# ).first()

				# print('connection Received location--->>>>>>',connection) 
				
				if connection:
					# print('Received location updateddd', connection)
					# Prepare location update data
					location_update = {
						"receiver":connection.receiver.phone,
						'driver_id': user.id,
						'latitude': latitude,
						'longitude': longitude,
						'accuracy': accuracy,
						'speed': speed,
						'timestamp': timestamp
					}
					# print('connection',connection.receiver)
					
					# Send to rider
					# self.send_group(
					# 	connection.receiver.phone,
					# 	'location.rider.update',
					# 	location_update
					# )

					self.send_group(connection.receiver.phone, 'location.rider.update', location_update)
					# self.send_group(connection.sender.phone, 'location.rider.update', location_update)
					
					# Send confirmation to driver
					# self.send_group(
					# 	user.phone,
					# 	'location.rider.update.confirmed',
					# 	{'status': 'success'}
					# )
					
			except Exception as e:
				print(f'Error finding connection: {str(e)}')
				
		except Exception as e:
			print(f'Error in location update: {str(e)}')


	def receive_driver_location_update(self, data):
		# print('Received driver location update', data)
		try:
			# Get the user and location data
			user = self.scope['user']
			location_data = data.get('data')
			
			if not location_data:
				print('No location data received')
				return
				
			# Extract location details
			latitude = location_data.get('latitude')
			longitude = location_data.get('longitude')
			accuracy = location_data.get('accuracy')
			speed = location_data.get('speed')
			timestamp = location_data.get('timestamp')
			
			# Find active connection for the driver
			try:
				# connection = Connection.objects.filter(
				 
				# 	accepted=True,
				# 	sender__phone=user.phone,
				# 	# status__in=['DRIVER ACCEPTED', 'TRIP STARTED']
				# ).first()

				connection = Connection.objects.filter(
					receiver__phone=user.phone
				).first()
				# print('connection --location.driver.update ===',connection)
			 
				
				if connection:
					# Prepare location update data
					location_update = {
						'sender': connection.sender.phone, 
						'receiver': connection.receiver.phone, 
						'latitude': latitude,
						'longitude': longitude,
						'accuracy': accuracy,
						'speed': speed,
						'timestamp': timestamp ,
						'from':'driver'
					}
					

					# Send to rider
					# self.send_group(
					# 	connection.receiver.phone,
					# 	'location.rider.update',
					# 	location_update
					# )

					# self.send_group(connection.receiver.phone, 'location.rider.update', location_update)
					self.send_group(connection.sender.phone, 'location.driver.update', location_update)
					
					# Send confirmation to driver
					# self.send_group(
					# 	user.phone,
					# 	'location.rider.update.confirmed',
					# 	{'status': 'success'}
					# )
					
			except Exception as e:
				print(f'Error finding connection: {str(e)}')
				
		except Exception as e:
			print(f'Error in location update: {str(e)}')

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
		
	def receive_request_cancel(self, data):
		# print("data",data)
		connection_id = data.get('connectionId')
		# 
		try:
			# Find and delete the connection
			connection = Connection.objects.get(id=connection_id)
			 
			# Store phones before deletion for notifications
			sender_phone = connection.sender.phone
			receiver_phone = connection.receiver.phone
			
			# Delete the connection
			connection.delete()
			
			# Notify both parties about the cancellation
			cancel_data = {
				'id': connection_id,
				'status': 'cancelled',
				"sender_phone":connection.sender.phone,
				"receiver_phone":connection.receiver.phone
			}
			
			self.send_group(sender_phone, 'request.cancel', cancel_data)
			self.send_group(receiver_phone, 'request.cancel', cancel_data)
			
		except Connection.DoesNotExist:
			print('Error: Connection not found')
			pass


