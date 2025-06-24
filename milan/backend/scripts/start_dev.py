#!/usr/bin/env python
"""
Development server startup script with Daphne (no Redis required)
"""
import os
import sys
import subprocess

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def start_server():
    """Start the development server with Daphne"""
    print("🚀 Starting Feedback Tool Development Server with Daphne...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/sse/{user_id}/")
    print("💾 Using in-memory channel layer (no Redis required)")
    print("🔗 Connected to Render PostgreSQL Database")
    print("⚠️  Note: Real-time features work only on single server instance")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found!")
        print("💡 Make sure you're running this from the backend/ directory")
        return
    
    try:
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        
        # Run Daphne server
        subprocess.run([
            sys.executable, "manage.py", "runserver", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        print("\n💡 Make sure you have installed all dependencies:")
        print("pip install -r requirements.txt")
    except FileNotFoundError:
        print("❌ Python not found in PATH")

if __name__ == "__main__":
    start_server()
