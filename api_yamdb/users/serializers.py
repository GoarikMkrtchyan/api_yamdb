from rest_framework import serializers
from users.models import User
from .constants import EMAIL_LENGTH, MAX_LENGTH
from .utils import send_confirmation_code
from .validators import validate_username, validate_username_format


class UserSerializer(serializers.ModelSerializer):
    """Serializer user."""
    email = serializers.EmailField(max_length=EMAIL_LENGTH, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']

    def validate(self, data):
        email = data.get('email')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'User with this email or username already exists.')

        return data


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin actions."""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'bio', 'role', 'is_active']

    def validate_role(self, value):
        valid_roles = [User.USER, User.ADMIN, User.MODERATOR]
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Недопустимая роль: {value}."
                "Допустимые роли: {', '.join(valid_roles)}."
            )
        return value


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=EMAIL_LENGTH, required=True)
    username = serializers.SlugField(
        max_length=MAX_LENGTH, required=True,
        validators=[validate_username, validate_username_format])

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        user = User.objects.filter(email=email, username=username).first()

        if user:
            # Если пользователь уже существует, вернем его данные
            # (например, отправим новый код подтверждения)
            user.generate_confirmation_code()
            user.save()
            return data

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username уже существует.'}
            )
        return data

    def create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        # Генерация и отправка кода подтверждения
        user.generate_confirmation_code()
        send_confirmation_code(user)
        user.save()
        return user


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.SlugField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'confirmation_code']
