import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Feedback
from .serializers import FeedbackSerializer
from .channel_manager import channel_manager
import logging

logger = logging.getLogger(__name__)

class SSEConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        logger.info(f"WebSocket: Connection attempt for user: {self.user}")
        
        if isinstance(self.user, AnonymousUser):
            logger.warning("WebSocket: Anonymous user attempted connection - rejecting")
            await self.close(code=4001)
            return
        
        self.user_id = str(self.user.id)
        self.group_name = f"user_{self.user_id}"
        
        # Check if user already has a connection
        if channel_manager.is_user_connected(self.user.id):
            logger.warning(f"WebSocket: User {self.user_id} already connected, closing duplicate")
            await self.close(code=4002)
            return
        
        try:
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
                'user_id': self.user_id,
                'timestamp': asyncio.get_event_loop().time()
            }))
            
            logger.info(f"WebSocket: User {self.user_id} connected successfully")
            
            # Start heartbeat
            asyncio.create_task(self.heartbeat())
            
        except Exception as e:
            logger.error(f"WebSocket: Error during connection for user {self.user_id}: {e}")
            await self.close(code=4003)

    async def disconnect(self, close_code):
        logger.info(f"WebSocket: Disconnecting user {getattr(self, 'user_id', 'unknown')} (code: {close_code})")
        
        if hasattr(self, 'group_name'):
            # Leave user group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            
            # Remove from our manager
            if hasattr(self, 'user') and self.user and not isinstance(self.user, AnonymousUser):
                channel_manager.remove_user_connection(self.user.id, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming messages if needed"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            logger.info(f"WebSocket: Received {message_type} from user {getattr(self, 'user_id', 'unknown')}")
            
            # Handle ping/pong for connection testing
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': asyncio.get_event_loop().time()
                }))
        except json.JSONDecodeError:
            logger.warning("WebSocket: Invalid JSON received")

    async def heartbeat(self):
        """Send periodic heartbeat to keep connection alive"""
        try:
            heartbeat_count = 0
            while True:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                heartbeat_count += 1
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat',
                    'timestamp': asyncio.get_event_loop().time(),
                    'count': heartbeat_count
                }))
                
                # Stop heartbeat after 20 beats (10 minutes) to prevent infinite loops
                if heartbeat_count >= 20:
                    logger.info(f"WebSocket: Heartbeat limit reached for user {getattr(self, 'user_id', 'unknown')}")
                    break
                
        except Exception as e:
            logger.error(f"Heartbeat error for user {getattr(self, 'user_id', 'unknown')}: {e}")

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
