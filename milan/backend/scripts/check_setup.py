#!/usr/bin/env python
"""
Check if the development environment is properly set up with Render database
"""
import os
import sys
import django

# Add the parent directory to the path so we can import Django settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_setup():
    """Check if everything is properly configured"""
    print("🔍 Checking Feedback Tool Setup with Render Database...")
    print("-" * 50)
    
    # Check Django setup
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        print("✅ Django configuration: OK")
    except Exception as e:
        print(f"❌ Django configuration: {e}")
        print("💡 Make sure you're running from the backend directory")
        return False
    
    # Check database connection
    try:
        from django.db import connection
        connection.ensure_connection()
        print("✅ Render PostgreSQL connection: OK")
        
        # Get database info
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            print(f"📊 Database: {db_version.split(',')[0]}")
            
            # Check database name
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            print(f"🗄️  Database Name: {db_name}")
            
    except Exception as e:
        print(f"❌ Database connection: {e}")
        print("💡 Check your DATABASE_URL in .env file")
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
    
    # Check models and migrations
    try:
        from feedback.models import User, Feedback
        user_count = User.objects.count()
        feedback_count = Feedback.objects.count()
        print(f"✅ Models: {user_count} users, {feedback_count} feedbacks")
        
        # Check for pending migrations
        from django.core.management import execute_from_command_line
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
            migration_output = mystdout.getvalue()
            if '[X]' in migration_output:
                print("✅ Migrations: Up to date")
            else:
                print("⚠️  Migrations: Pending migrations found")
                print("💡 Run: python manage.py migrate")
        finally:
            sys.stdout = old_stdout
            
    except Exception as e:
        print(f"❌ Models: {e}")
        print("💡 Run: python manage.py migrate")
        return False
    
    # Check authentication backend
    try:
        from django.conf import settings
        backends = settings.AUTHENTICATION_BACKENDS
        if 'feedback.backends.EmailBackend' in backends:
            print("✅ Email authentication: Configured")
        else:
            print("⚠️  Email authentication: Not configured")
    except Exception as e:
        print(f"❌ Authentication backend: {e}")
    
    # Check sample data
    try:
        from feedback.models import User
        manager_exists = User.objects.filter(email='manager@company.com').exists()
        employee_exists = User.objects.filter(email='employee@company.com').exists()
        
        if manager_exists and employee_exists:
            print("✅ Sample data: Available")
            print("📧 Login with: manager@company.com / password")
        else:
            print("⚠️  Sample data: Not found")
            print("💡 Run: python scripts/create_sample_data.py")
    except Exception as e:
        print(f"❌ Sample data check: {e}")
    
    # Check environment variables
    try:
        from django.conf import settings
        if hasattr(settings, 'DATABASES'):
            db_config = settings.DATABASES['default']
            if 'render.com' in db_config.get('HOST', ''):
                print("✅ Environment: Connected to Render PostgreSQL")
            else:
                print("⚠️  Environment: Not using Render database")
        print(f"🔧 Debug mode: {settings.DEBUG}")
        print(f"🌐 Allowed hosts: {settings.ALLOWED_HOSTS}")
    except Exception as e:
        print(f"❌ Environment check: {e}")
    
    # Check for common issues
    print("\n🔧 Common Issues Check:")
    
    # Check if running from correct directory
    current_dir = os.path.basename(os.getcwd())
    if current_dir == 'backend':
        print("✅ Working directory: Correct (backend)")
    else:
        print("⚠️  Working directory: Run from backend/ directory")
    
    # Check if manage.py exists
    if os.path.exists('manage.py'):
        print("✅ Django project: manage.py found")
    else:
        print("❌ Django project: manage.py not found")
    
    print("-" * 50)
    print("🎉 Setup check complete!")
    print("\n🚀 To start the server:")
    print("   python manage.py runserver")
    print("   # or")
    print("   python scripts/start_dev.py")
    print("\n📧 Use email addresses as usernames for login")
    print("🔗 Connected to Render PostgreSQL database")
    
    return True

if __name__ == "__main__":
    check_setup()
