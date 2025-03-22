from django.urls import path
from .views import CommonQuestionListView, ComputeTestResultView, StatementOptionView, TestHistoryView

urlpatterns = [
    path('question_add', CommonQuestionListView.as_view()),
    path('questions/get/',CommonQuestionListView.as_view()),
    
    path('submit-test/', ComputeTestResultView.as_view(), name='submit-test'),

    path('statements-options-add/', StatementOptionView.as_view()),
    path('statements-options-get/', StatementOptionView.as_view()),

    path("test-history/<int:user_id>/", TestHistoryView.as_view(), name="test-history"),
]