from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView

from books.forms import AddBookForm
from books.models import Book, Genres

navbar = [{'title': "Home", 'url_name': 'home'},
        {'title': "Add Book", 'url_name': 'add_book'},
        {'title': "Feedback", 'url_name': 'feedback'},
]


class BookMainPage(TemplateView):
    template_name = 'books/index.html'

    books = Book.objects.filter(is_published=1)
    extra_context = {
        'title': 'Favourite Books',
        'navbar': navbar,
        'books': books,
    }


class AllPublishedBooks(ListView):
    template_name = 'books/books.html'
    context_object_name = 'books'
    extra_context = {
        'title': 'My Books',
        'navbar': navbar,
    }

    def get_queryset(self):
        return Book.objects.filter(is_published=1)

def add_book(request):
    if request.method == 'POST':
        form = AddBookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('books')
    else:
        form = AddBookForm()

    data = {
        'title': 'Add new book',
        'navbar': navbar,
        'form': form,
    }
    return render(request, 'books/add_book.html', context=data)


class DetailedBookInfo(DetailView):
    template_name = 'books/book_info.html'
    slug_url_kwarg = 'book_slug'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['book'].title
        context['navbar'] = navbar
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Book.published, slug=self.kwargs[self.slug_url_kwarg])

def feedback(request):
    data = {
        'title': 'Feedback',
        'navbar': navbar,
    }
    return render(request, 'books/feedback.html', context=data)

def show_book_tags(request, tag_slug):
    tag = get_object_or_404(Genres, slug=tag_slug)
    books = tag.genres.filter(is_published=Book.Status.PUBLISHED)

    data = {
        'title': f'Genre: {tag.genre}',
        'navbar': navbar,
        'books': books,
    }

    return render(request, 'books/books.html', context=data)




