from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from users.models import User

from .constants import EMAIL_LENGTH, MAX_LENGTH


class UserSerializer(serializers.ModelSerializer):
    """Serializer user."""
    email = serializers.EmailField(max_length=EMAIL_LENGTH)

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

    def validate_role(self, value):
        valid_roles = [User.USER, User.ADMIN, User.MODERATOR]
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Недопустимая роль: {value}."
                f"Допустимые роли: {', '.join(valid_roles)}."
            )
        return value


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin actions."""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'bio', 'role', 'is_active']


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=EMAIL_LENGTH, required=True)
    username = serializers.SlugField(max_length=MAX_LENGTH, required=True)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        if User.objects.filter(username=username).exists(
        ) and User.objects.filter(email=email).exists():
            return data

        if User.objects.filter(username=username).exists(
        ) or User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'User with this email or username already exists.')

        if username.lower() == 'me':
            raise serializers.ValidationError(
                {'username': 'This username is reserved.'})

        return data


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        conf_code = data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if user.confirmation_code != conf_code or timezone.now(
        ) > user.confirmation_code_expiration:
            raise serializers.ValidationError(
                {'confirmation_code': 'Invalid or expired confirmation code.'})

        return data
