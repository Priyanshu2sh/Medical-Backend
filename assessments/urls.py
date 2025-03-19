from django.urls import path
from .views import check_answers, get_mcq_questions

urlpatterns = [
    path('mcqs/', get_mcq_questions, name='get_mcqs'),
    path('mcqs/check/', check_answers, name='check_answers'),  # Updated to check multiple answers
]
