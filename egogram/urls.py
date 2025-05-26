from django.urls import path
from .views import EgogramTestCreateView, CategoryCreateView, EgogramStatementCreateView, EgogramStatementWithTestView, EgogramSTatementUpdateView,  EgogramStatementsWithTestView, AddStatementToTestView, EgogramResultView, UserResultHistoryView, EgogramTestGetForTest

urlpatterns = [
    path('tests/', EgogramTestCreateView.as_view(), name='egogram-test-create'),
    path('all-tests/', EgogramTestCreateView.as_view(), name='all-egogram-tests'),
    path('egogram-test/',EgogramTestGetForTest.as_view(), name='egogram-test-for-test'),


    path('categories/', CategoryCreateView.as_view(), name='egogram-category-create'),
    path('all-categories/', CategoryCreateView.as_view(), name='all-egogram-categories'),


    path('statements/', EgogramStatementCreateView.as_view(), name='egogram-statement-create'),
    path('all-statements/', EgogramStatementCreateView.as_view(), name='all-statements'),
    path('statements/<int:test_id>/', EgogramStatementWithTestView.as_view(), name='statements-by-test'),       
    path('egogram-statements/<int:statement_id>/', EgogramSTatementUpdateView.as_view()),       #
    path('egogram-statements/<int:statement_id>/delete/', EgogramSTatementUpdateView.as_view()),        #
    path('egogram-test/<int:test_id>/statements/', EgogramStatementsWithTestView.as_view(), name='egogram-test-statements'),        #

    path('add-statement-to-test/', AddStatementToTestView.as_view(), name='add-statement-to-test'),

    path('egogram-result/', EgogramResultView.as_view(), name='egogram-result'),
    path('egogram-history/user-id/<int:user_id>/', UserResultHistoryView.as_view(), name='egogram-history'),

]