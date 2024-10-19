from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookMainPage.as_view(), name='home'),
    path('addbook/', views.AddBook.as_view(), name='add_book'),
    path('feedback/', views.Feedback.as_view(), name='feedback'),
    path('feedback-success/', views.FeedbackSuccess.as_view(), name='feedback_success'),
    path('books/', views.AllPublishedBooks.as_view(), name='books'),
    path('book/<slug:book_slug>/', views.DetailedBookInfo.as_view(), name='book'),
    path('edit/<slug:book_slug>/', views.BookEdit.as_view(), name='edit_book'),
    path('edit-success/', views.BookEditSuccess.as_view(), name='edit_success'),
    path('delete/<slug:book_slug>/', views.BookDelete.as_view(), name='delete_book'),
    path('tag/<slug:tag_slug>/', views.BookGenres.as_view(), name='tag'),
]