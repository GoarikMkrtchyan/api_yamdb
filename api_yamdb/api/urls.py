from django.urls import path
from .views import RegisterView, LoginView, LogoutView, EmailVerificationView, VerifyCodeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('email-verify/', EmailVerificationView.as_view(), name='email-verify'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
]
