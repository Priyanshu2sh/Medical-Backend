from django.urls import path
from .views import EgogramTestCreateView, EgogramCategoryCreateView, EgogramStatementCreateView

urlpatterns = [
    path('tests/', EgogramTestCreateView.as_view(), name='egogram-test-create'),
    path('all-tests/', EgogramTestCreateView.as_view(), name='all-egogram-tests'),


    path('categories/', EgogramCategoryCreateView.as_view(), name='egogram-category-create'),
    path('all-categories/', EgogramCategoryCreateView.as_view(), name='all-egogram-categories'),


    path('statements/', EgogramStatementCreateView.as_view(), name='egogram-statement-create'),
    path('all-statements/', EgogramStatementCreateView.as_view(), name='all-statements'),

]