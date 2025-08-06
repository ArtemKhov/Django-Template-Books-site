import logging
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django_unique_slugify import unique_slugify


logger = logging.getLogger(__name__)


class PublishedManager(models.Manager):
    """
    Custom manager to return only published books.
    """
    def get_queryset(self):
        """
        Returns queryset filtered to only include published books.
        """
        return super().get_queryset().filter(is_published=Book.Status.PUBLISHED)


class Book(models.Model):
    """
    Model representing a book with title, description, publication status, genres, image, and author.
    """
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
        """
        String representation of the Book object (returns the title).
        """
        return self.title

    class Meta:
        verbose_name = 'Books'
        verbose_name_plural = 'Books'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def get_absolute_url(self):
        """
        Returns the URL to access a detail page for this book.
        """
        return reverse('book', kwargs={'book_slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Overridden save method to generate a unique slug from the book title.
        """
        slug_str = self.title
        unique_slugify(self, slug_str)
        super().save(*args, **kwargs)
        logger.info(f"Book '{self.title}' saved/updated (id={self.id})")


class Genres(models.Model):
    """
    Model representing a genre/tag for books.
    """
    genre = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        """
        String representation of the Genre object (returns the genre name).
        """
        return self.genre

    class Meta:
        verbose_name = 'Genres'
        verbose_name_plural = 'Genres'

    def get_absolute_url(self):
        """
        Returns the URL to access a list of books with this genre.
        """
        return reverse('tag', kwargs={'tag_slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Overridden save method to generate a unique slug from the genre name.
        """
        slug_str = self.genre
        unique_slugify(self, slug_str)
        super().save(*args, **kwargs)
        logger.info(f"Genre '{self.genre}' saved/updated (id={self.id})")


class Comment(models.Model):
    """
    Model representing a comment on a book, with support for likes and nested replies.
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(get_user_model(), related_name='comment_likes', blank=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        """
        String representation of the Comment object (shows author and content).
        """
        return f"{self.author} - {self.content}"

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        Overridden save method for Comment
        """
        super().save(*args, **kwargs)
        logger.info(f"Comment by '{self.author}' on book id={self.book.id} saved/updated (id={self.id})")


class LikedComment(models.Model):
    """
    Model representing a like on a comment by a user.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of the LikedComment object (shows user and comment).
        """
        return f"{self.user} - {self.comment}"

    def save(self, *args, **kwargs):
        """
        Overridden save method for LikedComment
        """
        super().save(*args, **kwargs)
        logger.info(f"LikedComment by '{self.user}' on comment id={self.comment.id} saved/updated (id={self.id})")
