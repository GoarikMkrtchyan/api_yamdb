from django.forms import ValidationError
from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment
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
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Serializer жанров."""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    """Serializer произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'
    
    def get_rating(self, obj):
        if obj.rating == 0 and not obj.reviews.exists():
            return None
        return obj.rating


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer отзывов."""

    author = serializers.CharField(source='author.username', read_only=True)

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

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date', 'review']
        read_only_fields = ['author', 'pub_date', 'review']

    def get_author(self, obj):
        # Возвращаем только имя пользователя
        return obj.author.username
