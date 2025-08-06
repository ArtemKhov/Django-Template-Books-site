# Navigation bar structure for the site
navbar = [{'title': "Home", 'url_name': 'home'},
        {'title': "All books", 'url_name': 'books'},
        {'title': "My books", 'url_name': 'user_books'},
        {'title': "Add Book", 'url_name': 'add_book'},
        {'title': "Feedback", 'url_name': 'feedback'},
]

class DataMixin:
    """
    Mixin to provide extra context data (like page title and navbar) to views.
    """
    page_title = None
    paginate_by = 4
    extra_context = {}

    def __init__(self):
        if self.page_title:
            self.extra_context['title'] = self.page_title

        if 'navbar' not in self.extra_context:
            self.extra_context['navbar'] = navbar

    def get_mixin_context(self, context, **kwargs):
        """
        Adds navbar and any additional keyword arguments to the context.
        """
        context['navbar'] = navbar
        context.update(kwargs)
        return context