from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer пользователя."""

    class Meta:
        model = User
        fields = ['username']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Serializer жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'category',
                  'description', 'genre', 'rating',)


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'category',
                  'description', 'genre',)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer отзывов."""

    author = serializers.CharField(source='author.username', read_only=True)
    score = serializers.IntegerField(validators=(MinValueValidator(1),
                                                 MaxValueValidator(10)))

    class Meta:
        model = Review
        fields = ['id', 'text', 'score', 'author', 'pub_date']
        read_only_fields = ['author', 'pub_date']

    def validate(self, data):
        """Проверка, что пользователь уже оставлял
        отзыв на это произведение."""
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')

        if (Review.objects.filter(title_id=title_id,
                                  author=request.user).exists()
                and request.method == 'POST'):
            raise ValidationError("Вы уже оставили отзыв на это произведение.")

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Serializer комментариев."""

    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only='True')

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']
        read_only_fields = ['author', 'pub_date']
