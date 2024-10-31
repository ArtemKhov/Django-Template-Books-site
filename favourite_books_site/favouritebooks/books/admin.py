from django.contrib import admin, messages
from .models import Book, Genres, Comment


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
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
        genres = ', '.join([genre.genre for genre in obj.genres.all()])
        return genres

    @admin.action(description='Publish selected Books')
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Book.Status.PUBLISHED)
        self.message_user(request, f'Change {count} entries.')

    @admin.action(description='Unpublish selected Books')
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Book.Status.DRAFT)
        self.message_user(request, f'{count} books withdrawn from publication.', messages.WARNING)


@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass



