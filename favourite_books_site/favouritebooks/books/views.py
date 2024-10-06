from django.shortcuts import render
from django.http import HttpResponse

from books.models import Book

navbar = [{'title': "Add Book", 'url_name': 'add_post'},
        {'title': "Feedback", 'url_name': 'feedback'},
]

def index(request):
    posts = Book.published.all()

    data = {
        'title': 'Favourite Books',
        'navbar': navbar,
        'posts': posts,
    }
    return render(request, 'books/index.html', context=data)

def about(request):
    data = {
        'title': 'About',
        'navbar': navbar,
    }
    return render(request, 'books/about.html', context=data)

def add_post(request):
    data = {
        'title': 'Add Post',
        'navbar': navbar,
    }
    return render(request, 'books/add_post.html', context=data)

def feedback(request):
    data = {
        'title': 'Feedback',
        'navbar': navbar,
    }
    return render(request, 'books/feedback.html', context=data)




