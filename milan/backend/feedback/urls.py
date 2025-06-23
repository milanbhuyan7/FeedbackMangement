from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User
    path('user/profile/', views.user_profile, name='user_profile'),
    path('team/', views.team_list, name='team_list'),
    
    # Feedback
    path('feedbacks/', views.FeedbackListCreateView.as_view(), name='feedback_list_create'),
    path('feedbacks/<int:pk>/', views.FeedbackDetailView.as_view(), name='feedback_detail'),
    path('feedbacks/<int:pk>/acknowledge/', views.acknowledge_feedback, name='acknowledge_feedback'),
    
    # Server-Sent Events (backward compatibility)
    path('sse/', views.SSEView.as_view(), name='sse_stream'),
]
