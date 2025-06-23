#!/usr/bin/env python
import os
import sys
import django

# Add the parent directory to the path so we can import Django settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

from django.contrib.auth import get_user_model
from feedback.models import Feedback
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def create_sample_data():
    print("Creating sample data...")
    
    # Create manager
    manager, created = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@company.com',
            'first_name': 'John',
            'last_name': 'Manager',
            'is_manager': True,
        }
    )
    if created:
        manager.set_password('password123')
        manager.save()
        print("Created manager user")
    
    # Create employees
    employee1, created = User.objects.get_or_create(
        username='employee',
        defaults={
            'email': 'employee@company.com',
            'first_name': 'Jane',
            'last_name': 'Employee',
            'is_manager': False,
            'manager': manager,
        }
    )
    if created:
        employee1.set_password('password123')
        employee1.save()
        print("Created employee1 user")
    
    employee2, created = User.objects.get_or_create(
        username='employee2',
        defaults={
            'email': 'bob@company.com',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'is_manager': False,
            'manager': manager,
        }
    )
    if created:
        employee2.set_password('password123')
        employee2.save()
        print("Created employee2 user")
    
    # Create sample feedback
    feedback1, created = Feedback.objects.get_or_create(
        employee=employee1,
        manager=manager,
        defaults={
            'strengths': 'Excellent communication skills and always meets deadlines. Shows great initiative in problem-solving and helps team members when needed.',
            'areas_to_improve': 'Could benefit from learning more advanced technical skills and taking on leadership roles in projects.',
            'sentiment': 'positive',
            'acknowledged': False,
        }
    )
    if created:
        print("Created feedback1")
    
    feedback2, created = Feedback.objects.get_or_create(
        employee=employee2,
        manager=manager,
        defaults={
            'strengths': 'Very reliable and detail-oriented. Great team player who helps others and maintains high quality work.',
            'areas_to_improve': 'Needs to work on time management and prioritizing tasks more effectively. Could be more proactive in communication.',
            'sentiment': 'neutral',
            'acknowledged': True,
            'acknowledged_at': timezone.now() - timedelta(days=1),
        }
    )
    if created:
        print("Created feedback2")
    
    feedback3, created = Feedback.objects.get_or_create(
        employee=employee1,
        manager=manager,
        defaults={
            'strengths': 'Shows improvement in technical skills and has been more proactive in recent projects.',
            'areas_to_improve': 'Continue working on presentation skills and confidence when speaking to clients.',
            'sentiment': 'positive',
            'acknowledged': True,
            'acknowledged_at': timezone.now() - timedelta(hours=2),
        }
    )
    if created:
        print("Created feedback3")
    
    print("Sample data creation completed!")
    print("\nLogin credentials:")
    print("Manager: manager / password123")
    print("Employee: employee / password123")
    print("Employee2: employee2 / password123")

if __name__ == '__main__':
    create_sample_data()
