import threading
import time
import json
from collections import defaultdict, deque
from typing import Dict, List, Any

class SSEManager:
    """Manages Server-Sent Events connections and message broadcasting"""
    
    def __init__(self):
        self.connections: Dict[int, bool] = {}  # user_id -> is_connected
        self.user_events: Dict[int, deque] = defaultdict(lambda: deque(maxlen=100))  # user_id -> events queue
        self.lock = threading.Lock()
    
    def add_connection(self, user_id: int):
        """Add a new SSE connection for a user"""
        with self.lock:
            self.connections[user_id] = True
            print(f"SSE: User {user_id} connected")
    
    def remove_connection(self, user_id: int):
        """Remove SSE connection for a user"""
        with self.lock:
            if user_id in self.connections:
                del self.connections[user_id]
                print(f"SSE: User {user_id} disconnected")
    
    def is_user_connected(self, user_id: int) -> bool:
        """Check if a user has an active SSE connection"""
        with self.lock:
            return self.connections.get(user_id, False)
    
    def send_to_user(self, user_id: int, event_type: str, data: Any):
        """Send an event to a specific user"""
        with self.lock:
            event = {
                'type': event_type,
                'data': data,
                'timestamp': time.time()
            }
            
            # Add event to user's queue
            self.user_events[user_id].append(event)
            print(f"SSE: Sent {event_type} to user {user_id}")
    
    def send_to_multiple_users(self, user_ids: List[int], event_type: str, data: Any):
        """Send an event to multiple users"""
        for user_id in user_ids:
            self.send_to_user(user_id, event_type, data)
    
    def get_events_for_user(self, user_id: int) -> List[Dict]:
        """Get and clear pending events for a user"""
        with self.lock:
            events = list(self.user_events[user_id])
            self.user_events[user_id].clear()
            return events
    
    def broadcast_to_all(self, event_type: str, data: Any):
        """Broadcast an event to all connected users"""
        with self.lock:
            connected_users = list(self.connections.keys())
            for user_id in connected_users:
                self.send_to_user(user_id, event_type, data)
    
    def get_connected_users(self) -> List[int]:
        """Get list of all connected user IDs"""
        with self.lock:
            return list(self.connections.keys())
    
    def cleanup_old_events(self, max_age_seconds: int = 3600):
        """Clean up old events (older than max_age_seconds)"""
        current_time = time.time()
        with self.lock:
            for user_id in list(self.user_events.keys()):
                events = self.user_events[user_id]
                # Filter out old events
                fresh_events = deque(
                    [event for event in events if current_time - event['timestamp'] < max_age_seconds],
                    maxlen=100
                )
                self.user_events[user_id] = fresh_events

# Global SSE manager instance
sse_manager = SSEManager()

# Background cleanup task
def cleanup_task():
    """Background task to clean up old events"""
    while True:
        time.sleep(300)  # Run every 5 minutes
        sse_manager.cleanup_old_events()

# Start cleanup task in background
cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
cleanup_thread.start()
