import logging
from captcha.fields import CaptchaField
from django import forms
from django.core.exceptions import ValidationError

from .models import Book, Comment, Genres

logger = logging.getLogger(__name__)


class AddBookForm(forms.ModelForm):
    """
    Form for adding a new book, including title, description, publication status, genres, and image.
    """
    genres = forms.ModelMultipleChoiceField(queryset=Genres.objects.all().order_by('genre'),
                                    required=False,
                                    label='Genres',
                                    widget=forms.SelectMultiple(attrs={'class': 'genres-option'}))

    class Meta:
        model = Book
        fields = ['title', 'description', 'is_published', 'genres', 'image']
        labels = {
            'title': 'Book name',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Opinion about the book'}),
            'image': forms.FileInput(attrs={'id':'file-upload'}),
        }

    def clean_title(self):
        """
        Validates that the book title does not exceed the maximum allowed length.
        """
        title = self.cleaned_data['title']
        title_length = 100
        if len(title) > title_length:
            logger.warning(f"Book title too long: '{title}' (length={len(title)})")
            raise ValidationError(f'The length of the Book name cannot exceed {title_length} characters')
        logger.info(f"Validated book title: '{title}'")
        return title


class FeedbackForm(forms.Form):
    """
    Form for submitting feedback, including name, email, message, and captcha.
    """
    name = forms.CharField(label='Name',
                           max_length=255,
                           widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.EmailField(label='Email',
                             widget=forms.TextInput(attrs={'placeholder': 'Your Email'}))
    content = forms.CharField(label='Message',
                              widget=forms.Textarea(attrs={'placeholder': 'Provide feedback in this field'}))
    captcha = CaptchaField()


class CommentCreateForm(forms.ModelForm):
    """
    Form for creating a comment on a book.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Add comment ...',
                                             'style': 'height: 150px;'})
        }
        labels = {
            'content': '',
        }

    def save(self, commit=True):
        """
        Saves the comment instance. If commit is True, saves to the database.
        """
        comment = super(CommentCreateForm, self).save(commit=False)
        if commit:
            comment.save()
            logger.info(f"Comment saved via form by user {comment.author}")
        return comment