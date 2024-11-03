from books.utils import navbar


def get_books_context(request):
    return {'navbar': navbar}

