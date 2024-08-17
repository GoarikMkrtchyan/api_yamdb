from django.contrib.auth import get_user_model
from django.forms import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyCodeSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


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

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer отзывов."""

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
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']
