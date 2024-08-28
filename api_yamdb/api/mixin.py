from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet

from .permissions import IsAdmin, ReadOnly


class CategoryGenreMixinViewSet(
        ListModelMixin,
        CreateModelMixin,
        DestroyModelMixin,
        GenericViewSet):
    """Миксин для ViewSet категорий и жанров."""

    permission_classes = (IsAdmin | ReadOnly,)
    filter_backends = [SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
