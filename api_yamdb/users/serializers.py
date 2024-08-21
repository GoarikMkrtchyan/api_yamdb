from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer user."""
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        known_username = User.objects.filter(username=username)
        known_email = User.objects.filter(email=email)
        if known_username.exists():
            if (known_username.first().email != email):
                raise serializers.ValidationError()
        if known_email.exists():
            if (known_email.first().username != username):
                raise serializers.ValidationError()
        return data

    def validate_role(self, value):

        valid_roles = ['admin', 'user', 'moderator']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Недопустимая роль: {value}."
                f"Допустимые роли: {', '.join(valid_roles)}."
            )
        return value


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.SlugField(max_length=150)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        known_username = User.objects.filter(username=username)
        known_email = User.objects.filter(email=email)
        if known_username.exists():
            if (known_username.first().email != email):
                raise serializers.ValidationError()
        if known_email.exists():
            if (known_email.first().username != username):
                raise serializers.ValidationError()
        return data


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
