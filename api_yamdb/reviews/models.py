from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

from .validators import validate_year


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=50,
        choices=(
            ('user', 'User'),
            ('moderator', 'Moderator'),
            ('admin', 'Admin'),
        ),
        default='user',
    )
    confirmation_code = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        ordering = ['username']

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'
      

class Category(models.Model):
    """Model категории."""

    name = models.CharField('Наименование', max_length=256)
    slug = models.SlugField('Slug категории', max_length=50, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Model жанры."""

    name = models.CharField('Наименование', max_length=256)
    slug = models.SlugField('Slug жанра', max_length=50, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Model произведения."""

    name = models.CharField(
        'Наименование',
        max_length=256
    )
    year = models.IntegerField(
        'Год выпуска',
        validators=(validate_year,)
    )
    description = models.TextField('Описание')
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.year}"


class GenreTitle(models.Model):
    """Model жанр-произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='genre_titles'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='genre_titles'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title_id', 'genre_id'],
                name='unique_genre_title')
        ]

    def __str__(self):
        return f"{self.title} - {self.genre}"  

