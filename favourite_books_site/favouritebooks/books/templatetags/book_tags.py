from django import template
from books.models import Genres

register = template.Library()

@register.inclusion_tag('books/list_tags.html')
def show_all_tags():
    return {'tags': Genres.objects.all(), }