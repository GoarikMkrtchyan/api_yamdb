import secrets

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({'refresh': str(refresh),
                                 'access': str(refresh.access_token),
                                 'message': 'User logged in successfully'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'},
                                status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutViewSet(viewsets.ViewSet):
    """ViewSet для выхода пользователя."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "User logged out successfully"},
                            status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationViewSet(viewsets.ViewSet):
    """ViewSet для верификации email."""
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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
