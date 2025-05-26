from django.urls import path
from .views import CreateSessionAPI

urlpatterns = [
    path('counsellor-request/', CreateSessionAPI.as_view(), name='create-request'),
]