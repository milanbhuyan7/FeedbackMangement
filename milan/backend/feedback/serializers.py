from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Feedback
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_manager']

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
