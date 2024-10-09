from django.shortcuts import render
from django.http import HttpResponse

from books.models import Book

navbar = [{'title': "Add Book", 'url_name': 'add_book'},
        {'title': "Feedback", 'url_name': 'feedback'},
]

def index(request):

    data = {
        'title': 'Favourite Books',
        'navbar': navbar,
        'books': books,
    }
    return render(request, 'books/index.html', context=data)

def books(request):
    books = Book.object.filter(is_published=1)

    data = {
        'title': 'My Books',
        'navbar': navbar,
        'books': books,
    }
    return render(request, 'books/books.html', context=data)

def add_book(request):
    data = {
        'title': 'Add new book',
        'navbar': navbar,
    }
    return render(request, 'books/add_book.html', context=data)

def feedback(request):
    data = {
        'title': 'Feedback',
        'navbar': navbar,
    }
    return render(request, 'books/feedback.html', context=data)




