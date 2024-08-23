from django.db import models

from users.models import User

from .constants import MAX_LENGHT_NAME, MAX_LENGHT_SLUG, STRING_LENGHT_TEXT
from .validators import validate_year


class Category(models.Model):
    """Model категории."""

    name = models.CharField(
        'Наименование',
        max_length=MAX_LENGHT_NAME
    )
    slug = models.SlugField(
        'Slug категории',
        max_length=MAX_LENGHT_SLUG,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:STRING_LENGHT_TEXT]


class Genre(models.Model):
    """Model жанры."""

    name = models.CharField(
        'Наименование',
        max_length=MAX_LENGHT_NAME
    )
    slug = models.SlugField(
        'Slug жанра',
        max_length=MAX_LENGHT_SLUG,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:STRING_LENGHT_TEXT]


class Title(models.Model):
    """Model произведения."""

    name = models.CharField(
        'Наименование',
        max_length=MAX_LENGHT_NAME
    )
    year = models.SmallIntegerField(
        'Год выпуска',
        validators=(validate_year,)
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True
    )
    description = models.TextField(
        'Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return f'{self.name[:STRING_LENGHT_TEXT]} - {self.year}'


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
        verbose_name = 'Жанр-Произведение'
        verbose_name_plural = 'Жанры-Произведения'

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    """Model Отзыв."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name="reviews")
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review')
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text[:STRING_LENGHT_TEXT]


class Comment(models.Model):
    """Model Комментарий."""

    review = models.ForeignKey(Review,
                               related_name='comments',
                               on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:STRING_LENGHT_TEXT]
