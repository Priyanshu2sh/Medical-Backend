from django.urls import path
from .views import BooksAPIView, BookDetailsAPIView,CodeReactionAPIView

urlpatterns = [
    path('', BooksAPIView.as_view()),
    path('<int:book_id>/', BooksAPIView.as_view()),
    path('book-details/', BookDetailsAPIView.as_view()),
    path('book-details/<int:user_id>/', BookDetailsAPIView.as_view()),
    path('book-details/delete/<int:code_id>', BookDetailsAPIView.as_view()),
    path('code-reaction/<int:user_id>/', CodeReactionAPIView.as_view()),
]
