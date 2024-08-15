import secrets

from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .mixin import CategoryGenreMixinViewSet
from .permissions import IsAdminOrReadOnly, IsStuffOrAuthor
from .serializers import (
    RegisterSerializer, LoginSerializer, EmailVerificationSerializer,
    VerifyCodeSerializer, CategorySerializer, GenreSerializer,
    TitleSerializer, ReviewSerializer, CommentSerializer,
)
from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = request.data['token']
            token_obj = RefreshToken(token)
            token_obj.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        confirmation_code = secrets.token_urlsafe(8)[:6]
        # Отправка письма с кодом подтверждения
        send_mail(
            'Ваш код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

        return Response({'message': 'Код подтверждения отправлен на email'})


class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        # Проверка кода подтверждения (предполагается, что он хранится в базе данных или кэше)
        if confirmation_code == '123456':
            user = User.objects.get(username=username)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid confirmation code'}, status=status.HTTP_400_BAD_REQUEST)


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


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsStuffOrAuthor,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        if title_id is not None:
            return Review.objects.filter(title_id=title_id)
        return Review.objects.none()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = Title.objects.get(pk=title_id)
        review = serializer.save(title=title, author=self.request.user)
        review.title.update_rating()

    def perform_update(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = Title.objects.get(pk=title_id)
        review = serializer.save(title=title, author=self.request.user)
        review.title.update_rating()

    def perform_destroy(self, instance):
        title = instance.title
        super().perform_destroy(instance)
        title.update_rating()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsStuffOrAuthor,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        if review_id is not None:
            return Comment.objects.filter(review_id=review_id)
        return Comment.objects.none()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = Review.objects.get(pk=review_id)
        serializer.save(review=review, author=self.request.user)

    def perform_update(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = Review.objects.get(pk=review_id)
        serializer.save(review=review, author=self.request.user)
