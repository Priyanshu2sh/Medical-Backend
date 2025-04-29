from django.urls import path
from .views import CommonQuestionListView, ComputeTestResultView, StatementOptionView, TestHistoryView, QuizNameView, NewQuizView, QuizResultView, QuizResultHistoryView, TestQuizNameView, QuizAllQuestionView, QuizByTypeView, McqQuizCreateView, McqQuestionCreateView,  McqQuestionsByQuizForTestView, McqQuestionsByQuizIdView,McqQuestionsByTypeView, McqQuizBytypeView,McqQuizResultAPIView, McqQuizResultHistoryView

urlpatterns = [
    path('question_add', CommonQuestionListView.as_view()),
    path('questions/get/',CommonQuestionListView.as_view()),
    
    path('submit-test/', ComputeTestResultView.as_view(), name='submit-test'),

    path('statements-options-add/', StatementOptionView.as_view()),
    path('statements-options-get/', StatementOptionView.as_view()),

    path("test-history/<int:user_id>/", TestHistoryView.as_view(), name="test-history"),


    path('quiz-name/', QuizNameView.as_view(), name="quiz-name" ),
    path('quiz-name-get/', QuizNameView.as_view(), name="quiz-name-get" ),
    path('quiz/type/<str:quiz_type>/', QuizByTypeView.as_view(), name='quiz-by-type'),


    path('test-quiz-name/',TestQuizNameView.as_view(), name="test-quiz-name"),

    path('new-quiz/', NewQuizView.as_view(), name="new-quiz" ),

    #get only 20 questions for test
    path('new-quiz/<int:quiz_id>/', NewQuizView.as_view(), name='newquiz-by-id'),

    #for get all questions
    path('quiz/<int:quiz_id>/questions/', QuizAllQuestionView.as_view(), name='quiz-questions'), 

    path('quiz/<int:quiz_id>/question/<int:pk>/', NewQuizView.as_view(), name='update-quiz-question'),
    path('quiz/question/<int:id>/delete/', NewQuizView.as_view(), name='delete-quiz-question'),
    path('quiz-results/', QuizResultView.as_view(), name='quiz-results'),
    path('quiz/results/user/<int:user_id>/', QuizResultHistoryView.as_view(), name='user-quiz-history'),


    #for mcq quiz

    path('mcq-quiz/', McqQuizCreateView.as_view(), name='create-quiz'),
    path('mcq-quizzes/', McqQuizCreateView.as_view(), name='get-mcq-quizzes'),
    path('mcq-quiz/type/<str:type>/', McqQuizBytypeView.as_view(), name='mcq-quiz-by-type'),
    # path('mcq-quizzes/<int:quiz_id>/', McqQuestionCreateView.as_view(), name='get-mcq-quiz'),
    path('quiz/delete/<int:quiz_id>/', McqQuizCreateView.as_view(), name='quiz-delete'),

    path('mcq-question/', McqQuestionCreateView.as_view(), name='create-question'),
    path('mcq-questions/', McqQuestionCreateView.as_view(), name='mcq-questions-list'),     #for get all questions
    path('mcq-quiz/<int:quiz_id>/questions/', McqQuestionsByQuizForTestView.as_view(), name='mcq-questions-by-quiz'),
    path('mcq-questions/<int:question_id>/edit/', McqQuestionCreateView.as_view(), name='mcq-question-edit'),
    path('mcq-questions/<int:question_id>/delete/', McqQuestionCreateView.as_view(), name='mcq-question-delete'),
    
    path('mcq-quiz/<int:quiz_id>/questions-all/', McqQuestionsByQuizIdView.as_view(), name='mcq-questions-by-quiz-id'),
    path('mcq-questions/type/<str:type>/',McqQuestionsByTypeView.as_view(), name='mcq-questions-by-type'),
    
    path('submit-mcq-quiz/', McqQuizResultAPIView.as_view(), name='submit-quiz'),
    path('mcq-result-history/<int:user_id>/', McqQuizResultHistoryView.as_view(), name='mcq-result-history'),

]   