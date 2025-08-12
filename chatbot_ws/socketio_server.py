import os
import django
import socketio

# Set up Django settings so that you can import models if needed
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_books.settings")
django.setup()

# Create Socket.IO server (async mode for WebRTC signaling)
sio = socketio.AsyncServer(
    cors_allowed_origins="*",  # Allow any frontend origin (for local dev)
    async_mode="asgi",
    ping_interval=25,
    ping_timeout=60,
    logger=True,
    engineio_logger=True
)

# ASGI app for Django + Socket.IO
app = socketio.ASGIApp(sio)

# -----------------------------
# SOCKET.IO EVENTS
# -----------------------------
@sio.event
async def connect(sid, environ):
    print(f"🔌 Client connected: {sid}")
    await sio.emit("server_message", {"message": "Connected to Socket.IO server"}, to=sid)

@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")

# Example chat message event
@sio.event
async def message(sid, data):
    print(f"💬 Message from {sid}: {data}")
    await sio.emit("message", data)  # broadcast to all clients

# Example signaling event for WebRTC
@sio.event
async def signaling(sid, data):
    """
    Handles WebRTC signaling messages.
    data = {
        "to": "target_sid",
        "type": "offer/answer/candidate",
        "sdp": "...",
        "candidate": {...}
    }
    """
    print(f"📡 Signaling from {sid} to {data.get('to')}: {data}")
    target_sid = data.get("to")
    if target_sid:
        await sio.emit("signaling", data, to=target_sid)

# Room join for multiple peer WebRTC
@sio.event
async def join_room(sid, room):
    sio.enter_room(sid, room)
    print(f"🏠 {sid} joined room {room}")
    await sio.emit("room_joined", {"sid": sid, "room": room}, to=room)

@sio.event
async def leave_room(sid, room):
    sio.leave_room(sid, room)
    print(f"🚪 {sid} left room {room}")
    await sio.emit("room_left", {"sid": sid, "room": room}, to=room)
