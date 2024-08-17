from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, EmailVerificationViewSet, GenreViewSet,
                    LoginViewSet, LogoutViewSet, RegisterViewSet,
                    SignUpViewSet, TitleViewSet, TokenViewSet, UserProfileView,
                    VerifyCodeViewSet)

router_v1 = DefaultRouter()

router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'register', RegisterViewSet, basename='register')
router_v1.register(r'login', LoginViewSet, basename='login')
router_v1.register(r'logout', LogoutViewSet, basename='logout')
router_v1.register(r'email-verify', EmailVerificationViewSet,
                   basename='email-verify')
router_v1.register(r'verify-code', VerifyCodeViewSet, basename='verify-code')
router_v1.register(r'token', TokenViewSet, basename='token')

urlpatterns = [
    path('api/v1/', include(router_v1.urls)),
    path('api/v1/auth/token/', TokenViewSet.as_view({'post': 'create'}),
         name='token'),
    path('api/v1/users/me/', UserProfileView.as_view(), name='user-profile'),
    path('api/v1/auth/signup/',
         SignUpViewSet.as_view({'post': 'create'}), name='signup'),
]
