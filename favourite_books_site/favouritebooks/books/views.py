from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core import serializers
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseNotFound, HttpResponseRedirect, HttpResponseForbidden, \
    JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, UpdateView, DeleteView, CreateView

from books.forms import AddBookForm, FeedbackForm, CommentCreateForm
from books.models import Book, Genres
from books.utils import DataMixin
from favouritebooks import settings


class BookMainPage(DataMixin, TemplateView):
    template_name = 'books/index.html'
    page_title = 'Favourite Books'


class AllPublishedBooks(DataMixin, ListView):
    template_name = 'books/books.html'
    context_object_name = 'books'
    page_title = 'All Books'

    def get_queryset(self):
        return Book.objects.filter(is_published=1)


class UserBooks(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'books/user_books.html'
    context_object_name = 'books'
    page_title = 'My Books'

    def get_queryset(self):
        user = self.request.user
        return Book.objects.filter(author=user)


class AddBook(LoginRequiredMixin, DataMixin, FormView):
    form_class = AddBookForm
    template_name = 'books/add_book.html'
    page_title = 'Add new book'
    success_url = reverse_lazy('user_books')

    def form_valid(self, form):
        new_book = form.save(commit=False)
        new_book.author = self.request.user
        form.save()
        return super().form_valid(form)


class DetailedBookInfo(DataMixin, DetailView):
    template_name = 'books/book_info.html'
    slug_url_kwarg = 'book_slug'
    context_object_name = 'book'
    form_class = CommentCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()

        context['comments'] = self.object.comments.all()
        paginator = Paginator(context['comments'], per_page=5)
        page_number = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context['comments_page'] = page_obj
        context['paginator'] = paginator
        return self.get_mixin_context(context, title=context['book'].title)

    # Return book's slug according to url (book/<slug:book_slug>/)
    def get_object(self, queryset=None):
        return get_object_or_404(Book, slug=self.kwargs[self.slug_url_kwarg])

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            book_slug = self.kwargs[self.slug_url_kwarg]
            book = get_object_or_404(Book, slug=book_slug)
            comment = form.save(commit=False)
            comment.book = book
            comment.author = request.user
            comment.save()
            return HttpResponseRedirect(reverse_lazy('book', kwargs={'book_slug': book_slug}))
        else:
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        book = self.get_object()
        if book.is_published != 1 and book.author != self.request.user:
            raise Http404("Access denied")
        return super(DetailedBookInfo, self).dispatch(request, *args, **kwargs)


class BookEdit(DataMixin, UpdateView):
    model = Book
    form_class = AddBookForm
    slug_url_kwarg = 'book_slug'
    template_name = 'books/edit_book.html'
    success_url = reverse_lazy('edit_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=f'Edit book: {context["book"].title}')

    def dispatch(self, request, *args, **kwargs):
        book = self.get_object()
        if book.author != self.request.user:
            raise Http404("You are not allowed to edit this Book")
        return super(BookEdit, self).dispatch(request, *args, **kwargs)


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

    def dispatch(self, request, *args, **kwargs):
        book = self.get_object()
        if book.author != self.request.user:
            raise Http404("You are not allowed to delete this Book")
        return super(BookDelete, self).dispatch(request, *args, **kwargs)


class Feedback(LoginRequiredMixin, DataMixin, FormView):
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


class UserBooksByGenres(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'books/user_books.html'
    context_object_name = 'books'

    def get_queryset(self):
        user = self.request.user
        genre_slug = self.kwargs.get('tag_slug')
        # Filter books by user and selected genre
        return Book.objects.filter(author=user, genres__slug=genre_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Genres.objects.filter(
            id__in=Book.objects.filter(author=self.request.user).values_list('genres', flat=True)).distinct()
        tag = Genres.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='My books - Genre: ' + tag.genre)


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Page not found</h1>')
