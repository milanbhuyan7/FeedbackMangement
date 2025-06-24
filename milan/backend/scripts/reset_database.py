#!/usr/bin/env python
"""
Reset the database and create fresh sample data
"""
import os
import sys
import django

# Add the parent directory to the path so we can import Django settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

from django.contrib.auth import get_user_model
from feedback.models import Feedback
from django.db import transaction
from django.core.management import execute_from_command_line

User = get_user_model()

def reset_database():
    """Reset database and create fresh sample data"""
    print("🔄 Resetting Database...")
    print("⚠️  This will delete ALL existing data!")
    
    confirm = input("Type 'RESET' to continue: ")
    
    if confirm != 'RESET':
        print("❌ Operation cancelled")
        return False
    
    try:
        print("\n🗑️  Clearing all data...")
        with transaction.atomic():
            # Delete all feedback first (foreign key constraints)
            feedback_count = Feedback.objects.count()
            Feedback.objects.all().delete()
            print(f"   Deleted {feedback_count} feedback records")
            
            # Delete all users
            user_count = User.objects.count()
            User.objects.all().delete()
            print(f"   Deleted {user_count} user records")
        
        print("✅ Database cleared successfully!")
        
        # Reset auto-increment sequences
        print("\n🔧 Resetting ID sequences...")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE feedback_user_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE feedback_feedback_id_seq RESTART WITH 1;")
        print("✅ ID sequences reset")
        
        # Create fresh sample data
        print("\n📊 Creating fresh sample data...")
        from scripts.create_sample_data import create_sample_data
        success = create_sample_data()
        
        if success:
            print("\n🎉 Database reset completed successfully!")
            print("\n📧 Login credentials:")
            print("Manager: manager@company.com / password")
            print("Employee: employee@company.com / password")
            print("Employee2: bob@company.com / password")
            return True
        else:
            print("❌ Failed to create sample data")
            return False
            
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False

if __name__ == '__main__':
    reset_database()
