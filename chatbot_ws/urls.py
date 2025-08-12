from django.urls import path
from .views import mindcare_chat

urlpatterns = [
    path('voice-chat/', mindcare_chat, name='voice_chat_api'),
]