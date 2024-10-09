from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Book.Status.PUBLISHED)


class Book(models.Model):
    '''
    Book info
    '''
    class Status(models.IntegerChoices):
        PUBLISHED = 1, 'Published'
        DRAFT = 0, 'Draft'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(choices=Status.choices, default=Status.PUBLISHED)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    genre = models.ForeignKey('Genres', on_delete=models.PROTECT)

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def get_absolute_url(self):
        return reverse('book', kwargs={'book_slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Genres(models.Model):
    genre = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.genre




