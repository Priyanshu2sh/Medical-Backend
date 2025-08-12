# socket_server.py
import os
import django
import socketio
import base64

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_books.settings')
django.setup()

# Create Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')

# Create ASGI app for Socket.IO
socket_app = socketio.ASGIApp(sio)

# ========= Socket.IO EVENTS =========

@sio.event
async def connect(sid, environ):
    print(f"🔌 Client connected: {sid}")
    await sio.emit('server_message', {'type': 'connection', 'message': 'Connected successfully!'}, to=sid)

@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")

@sio.event
async def voice_data(sid, data):
    """
    Receives base64 encoded voice data from client,
    decodes it, and sends back the original + decoded text.
    """
    voice_b64 = data.get("voice", "")

    try:
        decoded_bytes = base64.b64decode(voice_b64)
        decoded_text = decoded_bytes.decode("utf-8", errors="ignore")
    except Exception:
        decoded_text = "[Error decoding base64]"

    print(f"🎤 Received voice (base64 length {len(voice_b64)}), decoded text: {decoded_text}")

    await sio.emit("server_message", {
        "type": "voice_response",
        "voice": voice_b64,
        "text": decoded_text
    }, to=sid)

@sio.event
async def message(sid, data):
    """Basic text echo"""
    print(f"📩 Received: {data}")
    await sio.emit('server_message', {'data': f"Echo: {data}"}, to=sid)
