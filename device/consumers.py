
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth.models import AnonymousUser
# from rest_framework_simplejwt.tokens import AccessToken
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Get token from query string
#         token = self.scope['query_string'].decode().split('=')[-1]
        
#         # Authenticate user
#         user = await self.get_user_from_token(token)
#         if user and not isinstance(user, AnonymousUser):
#             self.scope['user'] = user
#             await self.channel_layer.group_add(
#                 "notifications",
#                 self.channel_name
#             )
#             await self.accept()
#             print(f"✅ WebSocket connected for user: {user}")
#         else:
#             print("❌ WebSocket connection rejected: Invalid token")
#             await self.close()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             "notifications",
#             self.channel_name
#         )
#         print(f"🔌 WebSocket disconnected: {close_code}")

#     async def receive(self, text_data):
#         # Handle incoming messages if needed
#         pass

#     async def send_notification(self, event):
#         # Send notification to WebSocket
#         await self.send(text_data=json.dumps(event))

#     @database_sync_to_async
#     def get_user_from_token(self, token_key):
#         try:
#             token = AccessToken(token_key)
#             user = User.objects.get(id=token['user_id'])
#             return user
#         except Exception as e:
#             print(f"Token validation error: {e}")
#             return AnonymousUser()


# device/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from .models import Device, Notification

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get token from query string
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if token:
            try:
                # Verify the token
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.user = await self.get_user(user_id)
                
                if self.user and not isinstance(self.user, AnonymousUser):
                    self.group_name = f'notifications_{self.user.id}'
                    
                    # Join user-specific notification group
                    await self.channel_layer.group_add(
                        self.group_name,
                        self.channel_name
                    )
                    
                    await self.accept()
                    print(f"WebSocket connected for user: {self.user.username}")
                    
                    # Send initial connection status
                    await self.send(text_data=json.dumps({
                        'type': 'connection',
                        'status': 'connected'
                    }))
                else:
                    await self.close()
            except Exception as e:
                print(f"WebSocket auth error: {e}")
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # Handle incoming messages if needed
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
        except json.JSONDecodeError:
            pass

    async def notification_message(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'content': event['content']
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None