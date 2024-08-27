from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Comment, Genre, Review, Title
from .filters import TitleFilter
from .mixin import CategoryGenreMixinViewSet
from .permissions import IsAdmin, ReadOnly, IsStuffOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleCreateUpdateSerializer, TitleReadSerializer)


class CategoryViewSet(CategoryGenreMixinViewSet):
    """ViewSet категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixinViewSet):
    """ViewSet жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('name')
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = TitleReadSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin | ReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitleCreateUpdateSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet отзывов."""

    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsStuffOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    # Метод проверки тайтла. Возвращает тайтл или 404
    def check_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        title_id = self.check_title().pk
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title = self.check_title()
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet комментариев."""

    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsStuffOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def check_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        review_id = self.check_review().pk
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review = self.check_review()
        serializer.save(review=review, author=self.request.user)
