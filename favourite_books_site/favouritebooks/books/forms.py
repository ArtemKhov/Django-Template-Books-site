from captcha.fields import CaptchaField
from django import forms
from django.core.exceptions import ValidationError

from .models import Book, Genres

class AddBookForm(forms.ModelForm):
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
        title = self.cleaned_data['title']
        title_length = 100
        if len(title) > title_length:
            raise ValidationError(f'The length of the Book name cannot exceed {title_length} characters')

        return title

class FeedbackForm(forms.Form):
    name = forms.CharField(label='Name',
                           max_length=255,
                           widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.EmailField(label='Email',
                             widget=forms.TextInput(attrs={'placeholder': 'Your Email'}))
    content = forms.CharField(label='Message',
                              widget=forms.Textarea(attrs={'placeholder': 'Provide feedback in this field'}))
    captcha = CaptchaField()