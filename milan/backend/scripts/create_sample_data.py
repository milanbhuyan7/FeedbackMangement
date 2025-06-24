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
from django.db import transaction

User = get_user_model()

def create_sample_data():
    print("Creating sample data with email authentication...")
    print("🔗 Connected to Render PostgreSQL Database")
    
    try:
        with transaction.atomic():
            # Check if users already exist and clear if needed
            existing_users = User.objects.filter(
                email__in=['manager@company.com', 'employee@company.com', 'bob@company.com']
            )
            
            if existing_users.exists():
                print("⚠️  Found existing sample users. Cleaning up...")
                # Delete existing feedback first (foreign key constraint)
                Feedback.objects.filter(
                    manager__email__in=['manager@company.com'] 
                ).delete()
                # Delete existing users
                existing_users.delete()
                print("✅ Cleaned up existing sample data")
            
            # Create manager
            manager = User.objects.create_user(
                username='manager@company.com',
                email='manager@company.com',
                password='password',
                first_name='John',
                last_name='Manager',
                is_manager=True,
            )
            print("✅ Created manager user")
            
            # Create employees
            employee1 = User.objects.create_user(
                username='employee@company.com',
                email='employee@company.com',
                password='password',
                first_name='Jane',
                last_name='Employee',
                is_manager=False,
                manager=manager,
            )
            print("✅ Created employee1 user")
            
            employee2 = User.objects.create_user(
                username='bob@company.com',
                email='bob@company.com',
                password='password',
                first_name='Bob',
                last_name='Smith',
                is_manager=False,
                manager=manager,
            )
            print("✅ Created employee2 user")
            
            # Create sample feedback
            feedback1 = Feedback.objects.create(
                employee=employee1,
                manager=manager,
                strengths='Excellent communication skills and always meets deadlines. Shows great initiative in problem-solving and helps team members when needed.',
                areas_to_improve='Could benefit from learning more advanced technical skills and taking on leadership roles in projects.',
                sentiment='positive',
                acknowledged=False,
            )
            print("✅ Created feedback1")
            
            feedback2 = Feedback.objects.create(
                employee=employee2,
                manager=manager,
                strengths='Very reliable and detail-oriented. Great team player who helps others and maintains high quality work.',
                areas_to_improve='Needs to work on time management and prioritizing tasks more effectively. Could be more proactive in communication.',
                sentiment='neutral',
                acknowledged=True,
                acknowledged_at=timezone.now() - timedelta(days=1),
            )
            print("✅ Created feedback2")
            
            feedback3 = Feedback.objects.create(
                employee=employee1,
                manager=manager,
                strengths='Shows improvement in technical skills and has been more proactive in recent projects.',
                areas_to_improve='Continue working on presentation skills and confidence when speaking to clients.',
                sentiment='positive',
                acknowledged=True,
                acknowledged_at=timezone.now() - timedelta(hours=2),
            )
            print("✅ Created feedback3")
            
            print("\n🎉 Sample data creation completed successfully!")
            print("\n📧 Login credentials (use email as username):")
            print("Manager: manager@company.com / password")
            print("Employee: employee@company.com / password")
            print("Employee2: bob@company.com / password")
            print("\n🔗 Database: Connected to Render PostgreSQL")
            print("📊 Ready to test with real-time features!")
            
            # Display summary
            total_users = User.objects.count()
            total_feedback = Feedback.objects.count()
            print(f"\n📈 Database Summary:")
            print(f"   👥 Total Users: {total_users}")
            print(f"   💬 Total Feedback: {total_feedback}")
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        print("💡 This might be due to existing data conflicts.")
        print("🔧 Try running: python manage.py flush (WARNING: This will delete ALL data)")
        return False
    
    return True

def clear_all_data():
    """Clear all data from the database"""
    print("⚠️  WARNING: This will delete ALL data from the database!")
    confirm = input("Type 'yes' to continue: ")
    
    if confirm.lower() == 'yes':
        try:
            with transaction.atomic():
                Feedback.objects.all().delete()
                User.objects.all().delete()
                print("✅ All data cleared successfully!")
                return True
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            return False
    else:
        print("❌ Operation cancelled")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_all_data()
    else:
        create_sample_data()
