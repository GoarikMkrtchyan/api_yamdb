from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .mixin import CategoryGenreMixinViewSet
from .permissions import IsAdminOrReadOnly, IsStuffOrAuthor
from .serializers import (CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          ReviewSerializer,
                          TitleSerializer)
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
        title_id = get_object_or_404(Title, title_id='title_id')
        if title_id is not None:
            return Review.objects.filter(title_id=title_id)
        return Review.objects.none()

    def perform_create(self, serializer):
        title_id = get_object_or_404(Title, title_id='title_id')
        title = Title.objects.get(pk=title_id)
        review = serializer.save(title=title, author=self.request.user)
        review.title.update_rating()

    def perform_update(self, serializer):
        title_id = get_object_or_404(Title, title_id='title_id')
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
        review_id = get_object_or_404(Review, review_id='review_id')
        if review_id is not None:
            return Comment.objects.filter(review_id=review_id)
        return Comment.objects.none()

    def perform_create(self, serializer):
        review_id = get_object_or_404(Review, review_id='review_id')
        review = Review.objects.get(pk=review_id)
        serializer.save(review=review, author=self.request.user)

    def perform_update(self, serializer):
        review_id = get_object_or_404(Review, review_id='review_id')
        review = Review.objects.get(pk=review_id)
        serializer.save(review=review, author=self.request.user)
