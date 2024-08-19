from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User

from .validators import validate_year
from .constants import MAX_LENGHT_TEXT


class Category(models.Model):
    """Model категории."""

    name = models.CharField('Наименование', max_length=256)
    slug = models.SlugField('Slug категории', max_length=50, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_LENGHT_TEXT]


class Genre(models.Model):
    """Model жанры."""

    name = models.CharField('Наименование', max_length=256)
    slug = models.SlugField('Slug жанра', max_length=50, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_LENGHT_TEXT]


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

    rating = models.IntegerField(default=0)

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total_score = sum(review.score for review in reviews)
            self.rating = total_score / reviews.count()
        else:
            self.rating = None
        self.save()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name[:MAX_LENGHT_TEXT]} - {self.year}"


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


class Review(models.Model):
    """Model Отзыв."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name="reviews")
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(validators=(MinValueValidator(1),
                                            MaxValueValidator(10)))
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review')
        ]

    def __str__(self):
        return self.text[:MAX_LENGHT_TEXT]


class Comment(models.Model):
    """Model Комментарий."""

    review = models.ForeignKey(Review,
                               related_name='comments',
                               on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:MAX_LENGHT_TEXT]


class ReviewTitle(models.Model):
    """Model произведение-отзыв."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='review_titles'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='review_titles'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title_id', 'review_id'],
                name='unique_review_title')
        ]

    def __str__(self):
        return f"{self.title} - {self.review}"
