<<<<<<< HEAD
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, EmailVerificationViewSet, GenreViewSet,
                    LoginViewSet, LogoutViewSet, RegisterViewSet, TitleViewSet,
                    TokenViewSet, UserProfileView, VerifyCodeViewSet)
=======
from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import (
    CategoryViewSet, GenreViewSet, TitleViewSet, RegisterView,
    LoginView, LogoutView, EmailVerificationView, VerifyCodeView
)
>>>>>>> dbc8d050a315564b8d5f94ba096f581e6c85e70e

router_v1 = DefaultRouter()

router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
<<<<<<< HEAD
router_v1 = DefaultRouter()
router_v1.register(r'register', RegisterViewSet, basename='register')
router_v1.register(r'login', LoginViewSet, basename='login')
router_v1.register(r'logout', LogoutViewSet, basename='logout')
router_v1.register(r'email-verify', EmailVerificationViewSet, basename='email-verify')
router_v1.register(r'verify-code', VerifyCodeViewSet, basename='verify-code')
router_v1.register(r'token', TokenViewSet, basename='token')

urlpatterns = [
    path('api/v1/', include(router_v1.urls)),
    path('api/v1/users/me/', UserProfileView.as_view(), name='user-profile'),
=======

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('email-verify/', EmailVerificationView.as_view(), name='email-verify'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
>>>>>>> dbc8d050a315564b8d5f94ba096f581e6c85e70e
]
