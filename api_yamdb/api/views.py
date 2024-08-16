import secrets

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, CustomUser, Genre, Title

from .mixin import CategoryGenreMixinViewSet
from .permissions import IsAdminOrReadOnly
from .serializers import (CategorySerializer, CustomUserSerializer,
                          EmailVerificationSerializer, GenreSerializer,
                          LoginSerializer, RegisterSerializer, TitleSerializer,
                          TokenSerializer, VerifyCodeSerializer)


class RegisterViewSet(viewsets.ModelViewSet):
    """ViewSet для регистрации пользователя."""
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    http_method_names = ['get', 'post']


class TokenViewSet(viewsets.ViewSet):
    """ViewSet для получения токена."""
    def create(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid username"}, status=400)

        if user.confirmation_code != confirmation_code:
            return Response({"error": "Invalid confirmation code"}, status=400)

        token = str(RefreshToken.for_user(user))
        return Response({"token": token})


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginViewSet(viewsets.ViewSet):
    """ViewSet для входа пользователя."""
    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=401)


class LogoutViewSet(viewsets.ViewSet):
    """ViewSet для выхода пользователя."""
    permission_classes = [IsAuthenticated]

    def create(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token not provided'}, status=400)

        token_obj = RefreshToken(token)
        token_obj.blacklist()
        return Response(status=205)


class EmailVerificationViewSet(viewsets.ViewSet):
    """ViewSet для верификации email."""
    def create(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        confirmation_code = secrets.token_urlsafe(8)[:6]

        user, created = CustomUser.objects.get_or_create(email=email)
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            'Ваш код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

        return Response({'message': 'Код подтверждения отправлен на email'})


class VerifyCodeViewSet(viewsets.ViewSet):
    """ViewSet для проверки кода подтверждения."""
    def create(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = CustomUser.objects.get(username=username)
            if user.confirmation_code == confirmation_code:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Invalid confirmation code'}, status=400)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)


class CategoryViewSet(CategoryGenreMixinViewSet):
    """ViewSet категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixinViewSet):
    """ViewSet жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet произведений."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre__slug', 'category__slug')

    def perform_create(self, serializer):
        self.save_title(serializer)

    def perform_update(self, serializer):
        self.save_title(serializer)

    def save_title(self, serializer):
        category = get_object_or_404(
            Category, slug=self.request.data.get('category')
        )
        genre = Genre.objects.filter(
            slug__in=self.request.data.getlist('genre')
        )
        serializer.save(category=category, genre=genre)
