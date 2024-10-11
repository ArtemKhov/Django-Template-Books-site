from django import template
from django.db.models import Count

from books.models import Genres

register = template.Library()

@register.inclusion_tag('books/list_tags.html')
def show_all_tags():
    '''
    Select only those tags that are related to at least one book
    '''
    return {'tags': Genres.objects.annotate(total=Count('genres')).filter(total__gt=0)}