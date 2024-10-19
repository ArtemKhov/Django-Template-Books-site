from django.core.mail import EmailMessage
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView, UpdateView, DeleteView

from books.forms import AddBookForm, FeedbackForm
from books.models import Book, Genres
from books.utils import DataMixin
from favouritebooks import settings


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

class BookEdit(DataMixin, UpdateView):
    model = Book
    form_class = AddBookForm
    slug_url_kwarg = 'book_slug'
    template_name = 'books/edit_book.html'
    success_url = reverse_lazy('edit_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=f'Edit book: {context["book"].title}')

class BookEditSuccess(DataMixin, TemplateView):
    template_name = 'books/edit_book_success.html'
    page_title = 'Success'

class BookDelete(DataMixin, DeleteView):
    model = Book
    slug_url_kwarg = 'book_slug'
    template_name = 'books/delete_book.html'
    success_url = reverse_lazy('books')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=f'Delete book: {context["book"].title}')


class Feedback(DataMixin, FormView):
    form_class = FeedbackForm
    template_name = 'books/feedback.html'
    page_title = 'Feedback'
    success_url = reverse_lazy('feedback_success')

    def form_valid(self, form):
        # print(form.cleaned_data)

        user_email = form.cleaned_data.get('email')
        user_name = form.cleaned_data.get('name')
        user_message = form.cleaned_data.get('content')

        subject = f'Feedback from {user_email}'
        message = f'User name: {user_name}\nEmail: {user_email}\nMessage: {user_message}'

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER],
            reply_to=[user_email],
        )
        email.send(fail_silently=False)
        return super().form_valid(form)

class FeedbackSuccess(DataMixin, TemplateView):
    template_name = 'books/feedback_success.html'
    page_title = 'Success'

class BookGenres(DataMixin, ListView):
    template_name = 'books/books.html'
    context_object_name = 'books'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = Genres.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Genre: ' + tag.genre)

    def get_queryset(self):
        return Book.published.filter(genres__slug=self.kwargs['tag_slug']).prefetch_related('genres')




