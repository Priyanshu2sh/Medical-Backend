# asgi.py
import os
import django
from django.core.asgi import get_asgi_application
import socketio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_books.settings')
django.setup()

# Create Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')

# Create ASGI app for Socket.IO
socketio_app = socketio.ASGIApp(sio)

# Django ASGI app
django_asgi_app = get_asgi_application()

# Combined app
# This will route /socket.io/ to Socket.IO and everything else to Django
async def application(scope, receive, send):
    if scope['type'] in ('http', 'websocket') and scope['path'].startswith('/socket.io'):
        await socketio_app(scope, receive, send)
    else:
        await django_asgi_app(scope, receive, send)
