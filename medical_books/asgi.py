# import os
# import django
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from . import routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_books.settings')
# django.setup()

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": URLRouter(
#         routing.websocket_urlpatterns
#     ),
# })