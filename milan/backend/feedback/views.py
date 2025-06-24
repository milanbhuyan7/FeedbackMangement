from rest_framework import generics, permissions, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model, authenticate
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import time
from .models import Feedback
from .serializers import UserSerializer, FeedbackSerializer, AcknowledgeFeedbackSerializer, UserCreateSerializer
from .permissions import IsManagerOrReadOnly, IsEmployeeOrManager
from .channel_manager import channel_manager

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom serializer to allow email login"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change username field label to email
        self.fields['username'].help_text = 'Enter your email address'
    
    def validate(self, attrs):
        # Use email as username for authentication
        email_or_username = attrs.get('username')
        password = attrs.get('password')
        
        if email_or_username and password:
            # Try to authenticate with email
            user = authenticate(
                request=self.context.get('request'),
                username=email_or_username,
                password=password
            )
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                
                # Update attrs with the actual username for JWT processing
                attrs['username'] = user.username
            else:
                raise serializers.ValidationError('Invalid email or password.')
        
        return super().validate(attrs)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Add user info to response
            email_or_username = request.data.get('username')
            try:
                # Try to find user by email first, then username
                from django.db.models import Q
                user = User.objects.get(
                    Q(email__iexact=email_or_username) | Q(username__iexact=email_or_username)
                )
                response.data['user'] = UserSerializer(user).data
            except User.DoesNotExist:
                pass
        return response

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def team_list(request):
    """Get team members for managers"""
    if not request.user.is_manager:
        return Response(
            {'detail': 'Only managers can view team members.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    team_members = User.objects.filter(manager=request.user)
    serializer = UserSerializer(team_members, many=True)
    return Response(serializer.data)

class FeedbackListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            # Managers see feedback they've given
            return Feedback.objects.filter(manager=user)
        else:
            # Employees see feedback they've received
            return Feedback.objects.filter(employee=user)
    
    def perform_create(self, serializer):
        feedback = serializer.save()
        
        # Send real-time notification via Channels ONLY if users are connected
        employee_id = feedback.employee.id
        manager_id = feedback.manager.id
        
        # Serialize the feedback for sending
        feedback_data = FeedbackSerializer(feedback).data
        
        # Send to employee ONLY if they are connected
        if channel_manager.is_user_connected(employee_id):
            channel_manager.send_to_user(
                user_id=employee_id,
                event_type='new_feedback',
                data=feedback_data
            )
        
        # Send to manager ONLY if they are connected (for their dashboard update)
        if channel_manager.is_user_connected(manager_id):
            channel_manager.send_to_user(
                user_id=manager_id,
                event_type='feedback_created',
                data=feedback_data
            )

class FeedbackDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            return Feedback.objects.filter(manager=user)
        else:
            return Feedback.objects.filter(employee=user)
    
    def perform_update(self, serializer):
        feedback = serializer.save()
        
        # Send real-time notification for feedback update ONLY if users are connected
        employee_id = feedback.employee.id
        manager_id = feedback.manager.id
        
        feedback_data = FeedbackSerializer(feedback).data
        
        # Send to employee ONLY if connected
        if channel_manager.is_user_connected(employee_id):
            channel_manager.send_to_user(
                user_id=employee_id,
                event_type='feedback_updated',
                data=feedback_data
            )
        
        # Send to manager ONLY if connected
        if channel_manager.is_user_connected(manager_id):
            channel_manager.send_to_user(
                user_id=manager_id,
                event_type='feedback_updated',
                data=feedback_data
            )
    
    def perform_destroy(self, instance):
        employee_id = instance.employee.id
        manager_id = instance.manager.id
        feedback_id = instance.id
        
        instance.delete()
        
        # Send real-time notification for feedback deletion ONLY if users are connected
        if channel_manager.is_user_connected(employee_id):
            channel_manager.send_to_user(
                user_id=employee_id,
                event_type='feedback_deleted',
                data={'id': feedback_id}
            )
        
        if channel_manager.is_user_connected(manager_id):
            channel_manager.send_to_user(
                user_id=manager_id,
                event_type='feedback_deleted',
                data={'id': feedback_id}
            )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def acknowledge_feedback(request, pk):
    """Acknowledge feedback (employees only)"""
    try:
        feedback = Feedback.objects.get(pk=pk, employee=request.user)
    except Feedback.DoesNotExist:
        return Response(
            {'detail': 'Feedback not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if feedback.acknowledged:
        return Response(
            {'detail': 'Feedback already acknowledged.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = AcknowledgeFeedbackSerializer(feedback, data={'acknowledged': True})
    if serializer.is_valid():
        feedback = serializer.save()
        
        # Send real-time notification for acknowledgment ONLY if users are connected
        employee_id = feedback.employee.id
        manager_id = feedback.manager.id
        
        feedback_data = FeedbackSerializer(feedback).data
        
        # Send to manager ONLY if connected (they need to know it was acknowledged)
        if channel_manager.is_user_connected(manager_id):
            channel_manager.send_to_user(
                user_id=manager_id,
                event_type='feedback_acknowledged',
                data=feedback_data
            )
        
        # Send to employee ONLY if connected (for their dashboard update)
        if channel_manager.is_user_connected(employee_id):
            channel_manager.send_to_user(
                user_id=employee_id,
                event_type='feedback_acknowledged',
                data=feedback_data
            )
        
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Keep the SSE endpoint for backward compatibility
@method_decorator(csrf_exempt, name='dispatch')
class SSEView(View):
    """Server-Sent Events endpoint - now redirects to WebSocket"""
    
    def get(self, request):
        # Return instructions to use WebSocket instead
        response_data = {
            'message': 'SSE is now handled via WebSocket. Connect to ws://localhost:8000/ws/sse/{user_id}/ with token parameter.',
            'websocket_url': 'ws://localhost:8000/ws/sse/',
            'instructions': 'Use WebSocket connection with token as query parameter'
        }
        
        return StreamingHttpResponse(
            self._info_stream(response_data),
            content_type='text/event-stream'
        )
    
    def _info_stream(self, data):
        """Generate info stream"""
        yield f"data: {json.dumps(data)}\n\n"
