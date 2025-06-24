from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token):
    try:
        # Validate the token
        UntypedToken(token)
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        logger.info(f"WebSocket: Authenticated user {user.id} ({user.email})")
        return user
    except (InvalidToken, TokenError) as e:
        logger.warning(f"WebSocket: Invalid token - {e}")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"WebSocket: Authentication error - {e}")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        # Get token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            user = await get_user_from_token(token)
            scope['user'] = user
            logger.info(f"WebSocket: Setting user in scope - {user}")
        else:
            scope['user'] = AnonymousUser()
            logger.warning("WebSocket: No token provided")

        return await super().__call__(scope, receive, send)
