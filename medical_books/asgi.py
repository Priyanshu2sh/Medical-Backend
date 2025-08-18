# medical_books/asgi.py
import os
import django
from django.core.asgi import get_asgi_application

# import socketio app created in chatbot_ws
from chatbot_ws.socketio_server import app as socketio_app

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_books.settings")
django.setup()

django_asgi_app = get_asgi_application()

# Combined ASGI: route /socket.io/* to socketio_app, everything else to Django
async def application(scope, receive, send):
    """
    Routes:
      - if request path startswith /socket.io -> Socket.IO ASGI app (handles polling + websocket)
      - else -> Django ASGI app (HTTP)
    """
    path = scope.get("path", "")
    if path.startswith("/socket.io"):
        await socketio_app(scope, receive, send)
    else:
        await django_asgi_app(scope, receive, send)
