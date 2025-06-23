from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import threading
import time
from collections import defaultdict

class InMemoryChannelManager:
    """
    Simple in-memory channel manager for single-server deployments
    without Redis dependency
    """
    def __init__(self):
        self.connections = {}  # user_id -> channel_name
        self.user_groups = defaultdict(set)  # group_name -> set of channel_names
        self.channel_layer = get_channel_layer()
        self.lock = threading.Lock()

    def add_user_connection(self, user_id, channel_name):
        """Add a user connection"""
        with self.lock:
            self.connections[user_id] = channel_name
            group_name = f"user_{user_id}"
            self.user_groups[group_name].add(channel_name)
            print(f"Channel Manager: User {user_id} connected with channel {channel_name}")

    def remove_user_connection(self, user_id, channel_name):
        """Remove a user connection"""
        with self.lock:
            if user_id in self.connections:
                del self.connections[user_id]
            group_name = f"user_{user_id}"
            self.user_groups[group_name].discard(channel_name)
            if not self.user_groups[group_name]:
                del self.user_groups[group_name]
            print(f"Channel Manager: User {user_id} disconnected")

    def send_to_user(self, user_id, event_type, data):
        """Send event to a specific user"""
        if not self.channel_layer:
            print("Channel layer not available")
            return

        group_name = f"user_{user_id}"
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': self._convert_event_type(event_type),
                    'event_type': event_type,
                    'data': data
                }
            )
            print(f"Sent {event_type} to user {user_id}")
        except Exception as e:
            print(f"Error sending to user {user_id}: {e}")

    def send_to_multiple_users(self, user_ids, event_type, data):
        """Send event to multiple users"""
        for user_id in user_ids:
            self.send_to_user(user_id, event_type, data)

    def _convert_event_type(self, event_type):
        """Convert event type to consumer method name"""
        # Convert snake_case to method name format
        return event_type.replace('_', '.')

    def get_connected_users(self):
        """Get list of connected user IDs"""
        with self.lock:
            return list(self.connections.keys())

    def is_user_connected(self, user_id):
        """Check if user is connected"""
        with self.lock:
            return user_id in self.connections

# Global channel manager instance
channel_manager = InMemoryChannelManager()
