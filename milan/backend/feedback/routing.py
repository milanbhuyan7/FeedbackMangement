from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/sse/(?P<user_id>\w+)/$', consumers.SSEConsumer.as_asgi()),
]
