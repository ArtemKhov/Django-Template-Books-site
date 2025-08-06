import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import EmailMessage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import (Http404, HttpResponseNotFound, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (DeleteView, DetailView, FormView, ListView,
                                  TemplateView, UpdateView)

from books.forms import AddBookForm, CommentCreateForm, FeedbackForm
from books.models import Book, Comment, Genres
from books.utils import DataMixin
from favouritebooks import settings

logger = logging.getLogger(__name__)


class BookMainPage(DataMixin, TemplateView):
    """
    View for the main page of the Favourite Books site.
    """
    template_name = 'books/index.html'
    page_title = 'Favourite Books'


class AllPublishedBooks(DataMixin, ListView):
    """
    View to display all published books.
    """
    template_name = 'books/books.html'
    context_object_name = 'books'
    page_title = 'All Books'

    def get_queryset(self):
        """
        Returns queryset of all published books.
        """
        return Book.objects.filter(is_published=1)


class UserBooks(LoginRequiredMixin, DataMixin, ListView):
    """
    View to display books added by the current user.
    """
    template_name = 'books/user_books.html'
    context_object_name = 'books'
    page_title = 'My Books'

    def get_queryset(self):
        """
        Returns queryset of books authored by the current user.
        """
        user = self.request.user
        return Book.objects.filter(author=user)


class AddBook(LoginRequiredMixin, DataMixin, FormView):
    """
    View to handle adding a new book by a logged-in user.
    """
    form_class = AddBookForm
    template_name = 'books/add_book.html'
    page_title = 'Add new book'
    success_url = reverse_lazy('user_books')

    def form_valid(self, form):
        """
        Called when submitted form is valid. Sets the author to the current user.
        """
        new_book = form.save(commit=False)
        new_book.author = self.request.user
        form.save()
        logger.info(f"Book '{new_book.title}' added by user {self.request.user}")
        return super().form_valid(form)


class DetailedBookInfo(DataMixin, DetailView):
    """
    View to display detailed information about a book, including comments and comment form.
    """
    template_name = 'books/book_info.html'
    slug_url_kwarg = 'book_slug'
    context_object_name = 'book'
    form_class = CommentCreateForm

    def get_context_data(self, **kwargs):
        """
        Adds comments and comment form to the context.
        """
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
        """
        Returns the Book object based on the slug from the URL.
        """
        return get_object_or_404(Book, slug=self.kwargs[self.slug_url_kwarg])

    def post(self, request, *args, **kwargs):
        """
        Handles posting a new comment to the book. Requires authentication.
        """
        if not request.user.is_authenticated:
            return redirect('users:login')
        form = self.form_class(request.POST)
        if form.is_valid():
            book_slug = self.kwargs[self.slug_url_kwarg]
            book = get_object_or_404(Book, slug=book_slug)
            comment = form.save(commit=False)
            comment.book = book
            comment.author = request.user
            comment.save()
            logger.info(f"Comment added to book '{book.title}' by user {request.user}")
            return HttpResponseRedirect(reverse_lazy('book', kwargs={'book_slug': book_slug}))
        else:
            logger.warning(f"Invalid comment form submission by user {request.user}")
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        """
        Restricts access to unpublished books to the author only.
        """
        book = self.get_object()
        if book.is_published != 1 and book.author != self.request.user:
            logger.warning(f"Unauthorized access attempt to unpublished book '{book.title}' by user {self.request.user}")
            raise Http404("Access denied")
        return super(DetailedBookInfo, self).dispatch(request, *args, **kwargs)

class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View to handle deletion of a comment by its author or an admin.
    """
    def post(self, request, *args, **kwargs):
        """
        Deletes the comment if the user is the author or staff.
        """
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        if comment.author == request.user or request.user.is_staff:
            logger.info(f"Comment (id={comment.id}) deleted by user {request.user}")
            comment.delete()
        else:
            logger.warning(f"Unauthorized comment delete attempt by user {request.user}")
        current_page_number = request.GET.get('page', 1)
        redirect_url = f"{reverse_lazy('book', kwargs={'book_slug': comment.book.slug})}?page={current_page_number}"
        return redirect(redirect_url)

    def test_func(self):
        """
        Checks if the current user is allowed to delete the comment.
        """
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        return self.request.user == comment.author or self.request.user.is_staff

@method_decorator(login_required, name='dispatch')
class LikeCommentView(View):
    """
    View to handle liking and unliking comments via AJAX.
    """
    def post(self, request, *args, **kwargs):
        """
        Handles the like/unlike logic for a comment.
        """
        comment_id = kwargs.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            liked = False
        else:
            comment.likes.add(user)
            liked = True

        return JsonResponse({
            'liked': liked,
            'likes_count': comment.likes.count()
        })

class BookEdit(DataMixin, UpdateView):
    """
    View to handle editing a book by its author.
    """
    model = Book
    form_class = AddBookForm
    slug_url_kwarg = 'book_slug'
    template_name = 'books/edit_book.html'
    success_url = reverse_lazy('edit_success')

    def get_context_data(self, **kwargs):
        """
        Adds context for the edit book page.
        """
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=f'Edit book: {context["book"].title}')

    def dispatch(self, request, *args, **kwargs):
        """
        Restricts editing to the book's author only.
        """
        book = self.get_object()
        if book.author != self.request.user:
            raise Http404("You are not allowed to edit this Book")
        return super(BookEdit, self).dispatch(request, *args, **kwargs)


class BookEditSuccess(DataMixin, TemplateView):
    """
    View to display a success message after editing a book.
    """
    template_name = 'books/edit_book_success.html'
    page_title = 'Success'


class BookDelete(DataMixin, DeleteView):
    """
    View to handle deleting a book by its author.
    """
    model = Book
    slug_url_kwarg = 'book_slug'
    template_name = 'books/delete_book.html'
    success_url = reverse_lazy('books')

    def get_context_data(self, **kwargs):
        """
        Adds context for the delete book page.
        """
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=f'Delete book: {context["book"].title}')

    def dispatch(self, request, *args, **kwargs):
        """
        Restricts deletion to the book's author only.
        """
        book = self.get_object()
        if book.author != self.request.user:
            raise Http404("You are not allowed to delete this Book")
        return super(BookDelete, self).dispatch(request, *args, **kwargs)


class Feedback(LoginRequiredMixin, DataMixin, FormView):
    """
    View to handle feedback form submission by logged-in users.
    """
    form_class = FeedbackForm
    template_name = 'books/feedback.html'
    page_title = 'Feedback'
    success_url = reverse_lazy('feedback_success')

    def form_valid(self, form):
        """
        Sends feedback email to the site admin.
        """
        user_email = form.cleaned_data.get('email')
        user_name = form.cleaned_data.get('name')
        user_message = form.cleaned_data.get('content')
        logger.info(f"Feedback submitted by user {user_name} <{user_email}>")
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
    """
    View to display a success message after feedback submission.
    """
    template_name = 'books/feedback_success.html'
    page_title = 'Success'


class BookGenres(DataMixin, ListView):
    """
    View to display books filtered by a specific genre.
    """
    template_name = 'books/books.html'
    context_object_name = 'books'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Adds context for the genre page.
        """
        context = super().get_context_data(**kwargs)
        tag = Genres.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Genre: ' + tag.genre)

    def get_queryset(self):
        """
        Returns queryset of published books filtered by genre.
        """
        return Book.published.filter(genres__slug=self.kwargs['tag_slug']).prefetch_related('genres')


class UserBooksByGenres(LoginRequiredMixin, DataMixin, ListView):
    """
    View to display user's books filtered by a specific genre.
    """
    template_name = 'books/user_books.html'
    context_object_name = 'books'

    def get_queryset(self):
        """
        Returns queryset of user's books filtered by genre.
        """
        user = self.request.user
        genre_slug = self.kwargs.get('tag_slug')
        # Filter books by user and selected genre
        return Book.objects.filter(author=user, genres__slug=genre_slug)

    def get_context_data(self, **kwargs):
        """
        Adds context for the user's books by genre page.
        """
        context = super().get_context_data(**kwargs)
        context['tags'] = Genres.objects.filter(
            id__in=Book.objects.filter(author=self.request.user).values_list('genres', flat=True)).distinct()
        tag = Genres.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='My books - Genre: ' + tag.genre)


def page_not_found(request, exception):
    """
    Custom 404 error handler.
    """
    return HttpResponseNotFound('<h1>Page not found</h1>')
