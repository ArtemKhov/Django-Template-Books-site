from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookMainPage.as_view(), name='home'),
    path('addbook/', views.add_book, name='add_book'),
    path('feedback/', views.feedback, name='feedback'),
    path('books/', views.AddBook.as_view(), name='books'),
    path('book/<slug:book_slug>/', views.show_book, name='book'),
    path('tag/<slug:tag_slug>/', views.show_book_tags, name='tag'),
]