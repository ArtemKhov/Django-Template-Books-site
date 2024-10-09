from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('addbook/', views.add_book, name='add_book'),
    path('feedback/', views.feedback, name='feedback'),
    path('books/', views.books, name='books'),
]