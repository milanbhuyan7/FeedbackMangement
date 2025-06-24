from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import validate_email

class User(AbstractUser):
    email = models.EmailField(unique=True, validators=[validate_email])
    is_manager = models.BooleanField(default=False)
    manager = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='team_members'
    )
    
    # Make email required
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'feedback_user'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.email
    
    def save(self, *args, **kwargs):
        # If no username is provided, use email as username
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

class Feedback(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]
    
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_feedback'
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_feedback'
    )
    strengths = models.TextField()
    areas_to_improve = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='neutral')
    acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'feedback_feedback'
    
    def __str__(self):
        return f"Feedback for {self.employee} from {self.manager}"
