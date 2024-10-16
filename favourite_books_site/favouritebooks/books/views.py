from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView

from books.forms import AddBookForm, FeedbackForm
from books.models import Book, Genres
from books.utils import DataMixin


class BookMainPage(DataMixin, TemplateView):
    template_name = 'books/index.html'
    page_title = 'Favourite Books'

    books = Book.objects.filter(is_published=1)
    extra_context = {
        'books': books,
    }

class AllPublishedBooks(DataMixin, ListView):
    template_name = 'books/books.html'
    context_object_name = 'books'
    page_title = 'My Books'

    def get_queryset(self):
        return Book.objects.filter(is_published=1)


class AddBook(DataMixin, FormView):
    form_class = AddBookForm
    template_name = 'books/add_book.html'
    page_title = 'Add new book'
    success_url = reverse_lazy('books')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class DetailedBookInfo(DataMixin, DetailView):
    template_name = 'books/book_info.html'
    slug_url_kwarg = 'book_slug'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['book'].title)

    # show only published Book and return book's slug according to url (book/<slug:book_slug>/)
    def get_object(self, queryset=None):
        return get_object_or_404(Book.published, slug=self.kwargs[self.slug_url_kwarg])

class Feedback(DataMixin, FormView):
    form_class = FeedbackForm
    template_name = 'books/feedback.html'
    page_title = 'Feedback'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

class BookGenres(DataMixin, ListView):
    template_name = 'books/books.html'
    context_object_name = 'books'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = Genres.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Genre: ' + tag.genre)

    def get_queryset(self):
        return Book.published.filter(genres__slug=self.kwargs['tag_slug']).prefetch_related('genres')




