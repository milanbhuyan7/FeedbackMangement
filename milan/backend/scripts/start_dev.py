#!/usr/bin/env python
"""
Development server startup script with Daphne (no Redis required)
"""
import os
import sys
import subprocess

def start_server():
    """Start the development server with Daphne"""
    print("🚀 Starting Feedback Tool Development Server with Daphne...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/sse/{user_id}/")
    print("💾 Using in-memory channel layer (no Redis required)")
    print("⚠️  Note: Real-time features work only on single server instance")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Run Daphne server
        subprocess.run([
            sys.executable, "-m", "daphne",
            "-b", "0.0.0.0",
            "-p", "8000",
            "core.asgi:application"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        print("\n💡 Make sure you have installed all dependencies:")
        print("pip install -r requirements.txt")
    except FileNotFoundError:
        print("❌ Daphne not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "daphne"], check=True)
            print("✅ Daphne installed. Starting server...")
            subprocess.run([
                sys.executable, "-m", "daphne",
                "-b", "0.0.0.0",
                "-p", "8000",
                "core.asgi:application"
            ], check=True)
        except Exception as install_error:
            print(f"❌ Failed to install Daphne: {install_error}")

if __name__ == "__main__":
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    start_server()
