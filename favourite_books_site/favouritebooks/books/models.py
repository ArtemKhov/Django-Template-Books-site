from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django_unique_slugify import unique_slugify


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Book.Status.PUBLISHED)


class Book(models.Model):
    '''
    Book info
    '''

    class Status(models.IntegerChoices):
        PUBLISHED = 1, 'Published (available for all to view)'
        DRAFT = 0, 'Not published (available only you)'

    title = models.CharField(max_length=255,
                             verbose_name='Book name')
    description = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(choices=Status.choices, default=Status.PUBLISHED)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    genres = models.ManyToManyField('Genres',
                                    blank=True,
                                    related_name='genres',
                                    db_index=True,
                                    verbose_name='Genres')
    image = models.ImageField(upload_to='book_images/%Y/%m/%d/',
                              default=None,
                              blank=True,
                              null=True,
                              verbose_name='Book Image')
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.SET_NULL,
                               related_name='books',
                               null=True,
                               default=None)

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Books'
        verbose_name_plural = 'Books'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def get_absolute_url(self):
        return reverse('book', kwargs={'book_slug': self.slug})

    def save(self, *args, **kwargs):
        slug_str = self.title
        unique_slugify(self, slug_str)
        super().save(*args, **kwargs)


class Genres(models.Model):
    genre = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.genre

    class Meta:
        verbose_name = 'Genres'
        verbose_name_plural = 'Genres'

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})

    def save(self, *args, **kwargs):
        slug_str = self.genre
        unique_slugify(self, slug_str)
        super().save(*args, **kwargs)


class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(get_user_model(), related_name='comment_likes', blank=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author} - {self.content}"

    class Meta:
        ordering = ['-created_at']


class LikedComment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.comment}"
