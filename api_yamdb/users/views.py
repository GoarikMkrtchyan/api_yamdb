from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from .models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SignUpViewSet(APIView):
    """ViewSet для регистрации пользователя."""
    pass


class TokenViewSet(APIView):
    """ViewSet для регистрации пользователя."""
    pass
