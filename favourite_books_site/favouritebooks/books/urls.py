from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookMainPage.as_view(), name='home'),
    path('addbook/', views.AddBook.as_view(), name='add_book'),
    path('feedback/', views.Feedback.as_view(), name='feedback'),
    path('books/', views.AllPublishedBooks.as_view(), name='books'),
    path('book/<slug:book_slug>/', views.DetailedBookInfo.as_view(), name='book'),
    path('tag/<slug:tag_slug>/', views.BookGenres.as_view(), name='tag'),
]