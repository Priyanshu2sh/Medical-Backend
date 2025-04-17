from django.urls import path
from .views import CommonQuestionListView, ComputeTestResultView, StatementOptionView, TestHistoryView, QuizNameView, NewQuizView, QuizResultView

urlpatterns = [
    path('question_add', CommonQuestionListView.as_view()),
    path('questions/get/',CommonQuestionListView.as_view()),
    
    path('submit-test/', ComputeTestResultView.as_view(), name='submit-test'),

    path('statements-options-add/', StatementOptionView.as_view()),
    path('statements-options-get/', StatementOptionView.as_view()),

    path("test-history/<int:user_id>/", TestHistoryView.as_view(), name="test-history"),


    path('quiz-name/', QuizNameView.as_view(), name="quiz-name" ),
    path('quiz-name-get/', QuizNameView.as_view(), name="quiz-name-get" ),

    path('new-quiz/', NewQuizView.as_view(), name="new-quiz" ),
    path('new-quiz/<int:quiz_id>/', NewQuizView.as_view(), name='newquiz-by-id'),
    path('quiz/<int:quiz_id>/question/<int:pk>/', NewQuizView.as_view(), name='update-quiz-question'),
    path('quiz/question/<int:id>/delete/', NewQuizView.as_view(), name='delete-quiz-question'),
    path('quiz-results/', QuizResultView.as_view(), name='quiz-results'),

]   