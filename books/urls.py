from django.urls import path
from .views import BooksAPIView, BookDetailsAPIView

urlpatterns = [
    path('/', BooksAPIView.as_view()),
    path('<int:book_id>', BooksAPIView.as_view()),
    path('book-details', BookDetailsAPIView.as_view()),
    path('book-details/delete/<int:code_id>', BookDetailsAPIView.as_view()),
]
