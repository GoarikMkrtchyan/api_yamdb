from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import (
    CategoryViewSet, GenreViewSet, TitleViewSet, RegisterView,
    LoginView, LogoutView, EmailVerificationView, VerifyCodeView,
    ReviewViewSet, CommentViewSet
)

router_v1 = DefaultRouter()

router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('email-verify/', EmailVerificationView.as_view(), name='email-verify'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
]
