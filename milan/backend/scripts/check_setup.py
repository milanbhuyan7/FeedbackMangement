#!/usr/bin/env python
"""
Check if the development environment is properly set up
"""
import os
import sys
import django

def check_setup():
    """Check if everything is properly configured"""
    print("🔍 Checking Feedback Tool Setup...")
    print("-" * 40)
    
    # Check Django setup
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        print("✅ Django configuration: OK")
    except Exception as e:
        print(f"❌ Django configuration: {e}")
        return False
    
    # Check database connection
    try:
        from django.db import connection
        connection.ensure_connection()
        print("✅ Database connection: OK")
    except Exception as e:
        print(f"❌ Database connection: {e}")
        print("💡 Make sure PostgreSQL is running and database exists")
        return False
    
    # Check channels
    try:
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        if channel_layer:
            print("✅ Channels configuration: OK")
            print(f"📡 Channel layer: {channel_layer.__class__.__name__}")
        else:
            print("❌ Channels configuration: No channel layer found")
            return False
    except Exception as e:
        print(f"❌ Channels configuration: {e}")
        return False
    
    # Check models
    try:
        from feedback.models import User, Feedback
        user_count = User.objects.count()
        feedback_count = Feedback.objects.count()
        print(f"✅ Models: {user_count} users, {feedback_count} feedbacks")
    except Exception as e:
        print(f"❌ Models: {e}")
        print("💡 Run: python manage.py migrate")
        return False
    
    # Check sample data
    try:
        from feedback.models import User
        if User.objects.filter(username='manager').exists():
            print("✅ Sample data: Available")
        else:
            print("⚠️  Sample data: Not found")
            print("💡 Run: python scripts/create_sample_data.py")
    except Exception as e:
        print(f"❌ Sample data check: {e}")
    
    print("-" * 40)
    print("🎉 Setup check complete!")
    print("\n🚀 To start the server:")
    print("   python manage.py runserver")
    print("   # or")
    print("   python scripts/start_dev.py")
    
    return True

if __name__ == "__main__":
    check_setup()
