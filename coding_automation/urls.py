from django.urls import path
from .views import process_medical_document

urlpatterns = [
    path('process-medical-document/', process_medical_document, name='process_medical_document'),
]