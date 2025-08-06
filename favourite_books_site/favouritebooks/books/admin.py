import logging

from django.contrib import admin, messages

from .models import Book, Comment, Genres

logger = logging.getLogger(__name__)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface for the Book model, with custom actions and display options.
    """
    list_display = ['id', 'title', 'time_create', 'author', 'is_published', 'get_genres', 'slug']
    list_display_links = ['id', 'title']
    readonly_fields = ['slug']
    ordering = ['-time_create', 'title']
    actions = ['set_published', 'set_draft']
    search_fields = ['title', 'genres__genre']
    list_filter = ['genres__genre', 'is_published']
    filter_horizontal = ['genres']
    list_per_page = 10
    save_on_top = True

    def get_genres(self, obj):
        """
        Returns a comma-separated string of genres for the book.
        """
        genres = ', '.join([genre.genre for genre in obj.genres.all()])
        return genres

    @admin.action(description='Publish selected Books')
    def set_published(self, request, queryset):
        """
        Custom admin action to mark selected books as published.
        """
        count = queryset.update(is_published=Book.Status.PUBLISHED)
        self.message_user(request, f'Change {count} entries.')
        logger.info(f"Admin {request.user} published {count} books.")

    @admin.action(description='Unpublish selected Books')
    def set_draft(self, request, queryset):
        """
        Custom admin action to mark selected books as draft (unpublished).
        """
        count = queryset.update(is_published=Book.Status.DRAFT)
        self.message_user(request, f'{count} books withdrawn from publication.', messages.WARNING)
        logger.info(f"Admin {request.user} unpublished {count} books.")


@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    """
    Admin interface for the Genres model.
    """
    readonly_fields = ['slug']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for the Comment model.
    """
    pass



