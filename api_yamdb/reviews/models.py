from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .validators import validate_year


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
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    # метод для расчёта среднего рейтинга
    def update_rating(self):
        reviews = self.reviews.all()
        total_score = sum(review.score for review in reviews)
        self.rating = total_score / reviews.count() if reviews.exists() else 0
        self.save()

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


class Review(models.Model):
    """Model Отзыв."""
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    text = models.TextField()
    score = models.IntegerField(MinValueValidator(1), MaxValueValidator(10))
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'user'],
                                    name='unique_review')
        ]
    def __str__(self):
        return (self.text)


class Comment(models.Model):
    """Model Комментарий."""
    review = models.ForeignKey(Review,
                               related_name='comments',
                               on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return (self.text)