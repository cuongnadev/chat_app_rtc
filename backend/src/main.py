# backend/src/main.py
from services.chat_server import app

if __name__ == "__main__":
    print("🚀 Starting Chat App RTC Server...")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    try:
        app()
    except KeyboardInterrupt:
        print("\n✅ Server stopped successfully!")
    except Exception as e:
        print(f"❌ Server error: {e}")
