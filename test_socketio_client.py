import socketio
import asyncio
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Socket.IO client with proper configuration
sio = socketio.AsyncClient(
    logger=True,
    engineio_logger=True,
    reconnection=True,
    reconnection_attempts=5,
    reconnection_delay=1
)

@sio.event
async def connect():
    print("✅ Successfully connected to server")

@sio.event
async def connect_error(data):
    print(f"❌ Connection failed: {data}")

@sio.event
async def disconnect():
    print("⚠️ Disconnected from server")

@sio.event
async def assistant_response(data):
    print("\n💬 Assistant Response:")
    print(f"Text: {data.get('text')}")
    print(f"Audio chunks: {len(data.get('voice', []))}")

@sio.event
async def error(data):
    print(f"🚨 Error: {data.get('message')}")

async def main():
    try:
        server_url = 'http://192.168.1.57:8080'  # Try with localhost first
        print(f"Connecting to {server_url}...")
        
        await sio.connect(
            server_url,
            socketio_path='/socket.io/',  # Important if using Django with socket.io
            transports=['websocket'],    # Force WebSocket transport
            wait_timeout=10
        )
        
        # Test text message
        print("\nSending text message...")
        await sio.emit('text_message', {'text': 'Hello, I need mental health advice'})
        await asyncio.sleep(2)  # Wait for response
        
        # Test voice message (simulated)
        print("\nSending voice message...")
        await sio.emit('voice_message', {'voice': 'UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA='})
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"🔥 Exception: {str(e)}")
    finally:
        await sio.disconnect()

if __name__ == '__main__':
    asyncio.run(main())