from django.urls import path
from .views import CommonQuestionListView, ComputeTestResultView

urlpatterns = [
    path('question_add', CommonQuestionListView.as_view()),
    path('questions/',CommonQuestionListView.as_view()),
    path('submit-test/', ComputeTestResultView.as_view(), name='submit-test'),
]