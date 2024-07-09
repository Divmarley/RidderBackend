from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import json



class FoodConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()

        self.room_name = f"chat_{self.user.id}"
        self.room_group_name = f"chat_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'start_trip':
            # Handle startTrip event
            await self.start_trip()
        else:
            message = data['message']
            sender = data['sender']
            recipient = data['recipient']
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender,
                    'recipient': recipient
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        recipient = event['recipient']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'recipient': recipient
        }))


    @database_sync_to_async
    def get_user(self):
        return self.scope['user']


    