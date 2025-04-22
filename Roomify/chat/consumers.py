import json
from accounts.backends import User
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from .models import ChatRoom, ChatMessage
from rooms import *
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        if await self.verify_room_access():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            await self.mark_messages_as_read()
        else:
            await self.close(code=4003)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            # Add this case to handle read receipts
            if data.get('type') == 'mark_read':
                if await database_sync_to_async(self.room.mark_as_read)(self.user):
                    await self.send_chat_list_update(self.room, self.user.id)
                return
            
            message = data['message']
            sender_id = data['sender_id']
            room_id = data['room_id']

            timestamp = datetime.now()
            chat_room = await self.save_message(room_id, sender_id, message, timestamp)

            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id,
                    'timestamp': timestamp.isoformat(),
                    'sender_channel': self.channel_name
                }
            )

            await self.send_chat_list_update(chat_room, sender_id)
        except Exception as e:
            print(f"Error in receive: {str(e)}")

    async def chat_message(self, event):
        if self.channel_name != event['sender_channel']:
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': event['message'],
                'sender_id': event['sender_id'],
                'timestamp': event['timestamp']
            }))

    async def send_chat_list_update(self, chat_room, sender_id):
        await database_sync_to_async(chat_room.update_unread_status)()
        
        # Only notify the other user
        recipient_id = str(chat_room.seller.id) if str(sender_id) == str(chat_room.customer.id) else str(chat_room.customer.id)
        
        if str(sender_id) != recipient_id:  # Double-check we're not notifying sender
            await self.channel_layer.group_send(
                f'user_{recipient_id}_chats',
                {
                    'type': 'chat_list_update',
                    'room_id': chat_room.id,
                    'latest_message': chat_room.latest_message,
                    'has_unread': True,
                    'timestamp': datetime.now().isoformat()
                }
            )


    async def mark_messages_as_read(self):
        """Only notifies the OTHER user (receiver) when messages are read"""
        if await database_sync_to_async(self.room.mark_as_read)(self.user):
            other_user = self.room.seller if self.user == self.room.customer else self.room.customer
            await self.channel_layer.group_send(
                f'user_{other_user.id}_chats',
                {
                    'type': 'chat_list_update',
                    'room_id': self.room.id,
                    'latest_message': self.room.latest_message,
                    'has_unread': False,  # Force unread=false for receiver
                    'timestamp': datetime.now().isoformat()
                }
            )

    @database_sync_to_async
    def verify_room_access(self):
        try:
            self.room = ChatRoom.objects.filter(
                Q(id=self.room_id) & 
                (Q(customer=self.user) | Q(seller=self.user))
            ).select_related('customer', 'seller').first()
            return self.room is not None
        except Exception as e:
            print(f"Error verifying room access: {e}")
            return False

    @database_sync_to_async
    def save_message(self, room_id, sender_id, message, timestamp):
        try:
            sender = User.objects.get(id=sender_id)
            chat_room = ChatRoom.objects.select_related('customer', 'seller').get(id=room_id)
            current_user = self.scope['user']
            
            # Create message (explicitly unread)
            ChatMessage.objects.create(
                chat_room=chat_room,
                sender=sender,
                message=message,
                timestamp=timestamp,
                read=False
            )
            
            # Update room status - only unread for receiver
            chat_room.latest_message = message
            chat_room.has_unread_messages = (sender != current_user)
            chat_room.save()
            
            return chat_room
        except Exception as e:
            print(f"Error saving message: {e}")
            raise

class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}_chats'

        if not await self.verify_user_access():
            await self.close(code=4001)
            return


        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def chat_list_update(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat_list_update',
                'room_id': event['room_id'],
                'latest_message': event['latest_message'],
                'has_unread': event['has_unread'],
                'timestamp': event.get('timestamp')
            }))
        except Exception as e:
            print(f"Error sending chat list update: {str(e)}")

    @database_sync_to_async
    def verify_user_access(self):
        try:
            user = self.scope["user"]
            return user.is_authenticated and str(user.id) == self.user_id
        except Exception as e:
            print(f"Error verifying user access: {e}")
            return False