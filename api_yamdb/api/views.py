from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from .filters import TitleFilter
from .mixin import CategoryGenreMixinViewSet
from .permissions import IsAdminOrReadOnly, IsStuffOrAuthor
from .serializers import (CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          ReviewSerializer,
                          TitleReadSerializer,
                          TitleCreateUpdateSerializer)
from reviews.models import (Category,
                            Genre,
                            Title,
                            Review,
                            Comment)


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
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleCreateUpdateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet отзывов."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsStuffOrAuthor,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        # Получаем `title_id` из параметров запроса (URL)
        title_id = self.kwargs.get('title_id')
        if title_id is not None:
            return Review.objects.filter(title_id=title_id)
        return Review.objects.none()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(title=title, author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)



class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet комментариев."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsStuffOrAuthor,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        # Получаем `review_id` из параметров запроса (URL)
        review_id = self.kwargs.get('review_id')
        if review_id is not None:
            return Comment.objects.filter(review_id=review_id)
        return Comment.objects.none()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(review=review, author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
