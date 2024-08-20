from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer user."""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'role']
        read_only_fields = ['role',]


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        # Проверка уникальности email
        if User.objects.filter(email=email).exists():
            # Поскольку email должен быть уникальным, можем просто вернуть данные без исключения
            pass

        # Проверка уникальности username
        if User.objects.filter(username=username).exists():
            # Поскольку username должен быть уникальным, можем просто вернуть данные без исключения
            pass


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
