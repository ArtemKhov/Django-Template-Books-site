from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    data = {'title': 'Favourite Books'}
    return render(request, 'books/index.html', data)


