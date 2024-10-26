from django import template
from django.db.models import Count

from books.models import Genres, Book

register = template.Library()

@register.inclusion_tag('books/list_tags.html')
def show_all_tags():
    '''
    Select only those tags that are related to at least one book
    '''
    return {'tags': Genres.objects.annotate(total=Count('genres')).filter(total__gt=0)}


@register.inclusion_tag('books/list_user_tags.html', takes_context=True)
def show_user_tags(context):
    request = context['request']
    user = request.user
    # Get genre IDs related the current user's books
    user_genre_ids = Book.objects.filter(author=user).values_list('genres', flat=True)
    # Fetch distinct genres associated with the user's books
    tags = Genres.objects.filter(id__in=user_genre_ids).distinct()
    return {'tags': tags}