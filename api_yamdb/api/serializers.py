from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, CustomUser, Genre, Title

<<<<<<< HEAD

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role', 'confirmation_code')
=======
from reviews.models import Category, Genre, Title

User = get_user_model()
>>>>>>> dbc8d050a315564b8d5f94ba096f581e6c85e70e


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid username")

        # Валидация кода подтверждения
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Invalid confirmation code")

        # Генерация токена
        return {
            'token': str(AccessToken.for_user(user))
        }


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyCodeSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

<<<<<<< HEAD

=======
    
>>>>>>> dbc8d050a315564b8d5f94ba096f581e6c85e70e
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
