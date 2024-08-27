from rest_framework import serializers
from users.models import User
from .constants import EMAIL_LENGTH, MAX_LENGTH
from .utils import send_confirmation_code
import re


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

    # def validate_role(self, value):
    #     valid_roles = [User.USER, User.ADMIN, User.MODERATOR]
    #     if value not in valid_roles:
    #         raise serializers.ValidationError(
    #             f"Недопустимая роль: {value}."
    #             f"Допустимые роли: {', '.join(valid_roles)}."
    #         )
    #     return value


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
    username = serializers.CharField(max_length=MAX_LENGTH, required=True)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        # Проверяем, если уже есть пользователь
        # с таким email, но с другим username
        if User.objects.filter(email=email).exclude(username=username).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )

        # Проверяем, если уже есть пользователь
        # с таким username, но с другим email
        if User.objects.filter(username=username).exclude(email=email).exists():
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username уже существует.'}
            )

        if not re.match(r'^[\w.@+-]+\Z', username):
            raise serializers.ValidationError(
                {'username': 'Недопустимое имя пользователя'})

        if username.lower() == 'me':
            raise serializers.ValidationError(
                {'username': 'Это имя пользователя зарезервировано.'}
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
