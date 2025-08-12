from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('api/ws/example/', consumers.Consumer.as_asgi()),
]
