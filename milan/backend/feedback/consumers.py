import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Feedback
from .serializers import FeedbackSerializer
from .channel_manager import channel_manager

class SSEConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        self.user_id = str(self.user.id)
        self.group_name = f"user_{self.user_id}"
        
        # Join user group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Register connection in our manager
        channel_manager.add_user_connection(self.user.id, self.channel_name)
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'WebSocket connection established',
            'user_id': self.user_id
        }))
        
        # Start heartbeat
        asyncio.create_task(self.heartbeat())
        
        print(f"WebSocket: User {self.user_id} connected")

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            # Leave user group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            
            # Remove from our manager
            channel_manager.remove_user_connection(self.user.id, self.channel_name)
        
        print(f"WebSocket: User {getattr(self, 'user_id', 'unknown')} disconnected")

    async def receive(self, text_data):
        """Handle incoming messages if needed"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            print(f"WebSocket: Received {message_type} from user {self.user_id}")
            
            # Handle ping/pong for connection testing
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': asyncio.get_event_loop().time()
                }))
        except json.JSONDecodeError:
            print("WebSocket: Invalid JSON received")

    async def heartbeat(self):
        """Send periodic heartbeat to keep connection alive"""
        try:
            while True:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat',
                    'timestamp': asyncio.get_event_loop().time()
                }))
        except Exception as e:
            print(f"Heartbeat error: {e}")

    # Event handlers for different types of messages
    async def new_feedback(self, event):
        """Handle new feedback event"""
        await self.send(text_data=json.dumps({
            'type': 'new_feedback',
            'data': event['data']
        }))

    async def feedback_updated(self, event):
        """Handle feedback updated event"""
        await self.send(text_data=json.dumps({
            'type': 'feedback_updated',
            'data': event['data']
        }))

    async def feedback_deleted(self, event):
        """Handle feedback deleted event"""
        await self.send(text_data=json.dumps({
            'type': 'feedback_deleted',
            'data': event['data']
        }))

    async def feedback_acknowledged(self, event):
        """Handle feedback acknowledged event"""
        await self.send(text_data=json.dumps({
            'type': 'feedback_acknowledged',
            'data': event['data']
        }))

    async def feedback_created(self, event):
        """Handle feedback created event"""
        await self.send(text_data=json.dumps({
            'type': 'feedback_created',
            'data': event['data']
        }))

    # Generic event handler
    async def send_event(self, event):
        """Generic event sender"""
        await self.send(text_data=json.dumps({
            'type': event.get('event_type', 'message'),
            'data': event.get('data', {})
        }))
