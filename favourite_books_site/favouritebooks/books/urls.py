from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('addbook/', views.add_book, name='add_book'),
    path('feedback/', views.feedback, name='feedback'),
    path('books/', views.books, name='books'),
    path('book/<slug:book_slug>/', views.show_book, name='book'),
]