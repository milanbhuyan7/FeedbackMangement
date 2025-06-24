from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Feedback
from django.utils import timezone
from django.core.validators import validate_email

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_manager']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm', 'is_manager']
    
    def validate_email(self, value):
        validate_email(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Use email as username
        validated_data['username'] = validated_data['email']
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class FeedbackSerializer(serializers.ModelSerializer):
    employee = UserSerializer(read_only=True)
    manager = UserSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'employee', 'manager', 'employee_id', 'strengths', 
            'areas_to_improve', 'sentiment', 'acknowledged', 
            'created_at', 'updated_at', 'acknowledged_at'
        ]
        read_only_fields = ['manager', 'acknowledged', 'acknowledged_at']
    
    def create(self, validated_data):
        employee_id = validated_data.pop('employee_id')
        employee = User.objects.get(id=employee_id)
        
        # Ensure the employee is under the manager
        if not employee.manager == self.context['request'].user:
            raise serializers.ValidationError("You can only give feedback to your team members.")
        
        validated_data['employee'] = employee
        validated_data['manager'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Remove employee_id from validated_data if present (can't change employee)
        validated_data.pop('employee_id', None)
        return super().update(instance, validated_data)

class AcknowledgeFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['acknowledged', 'acknowledged_at']
        read_only_fields = ['acknowledged_at']
    
    def update(self, instance, validated_data):
        instance.acknowledged = True
        instance.acknowledged_at = timezone.now()
        instance.save()
        return instance
