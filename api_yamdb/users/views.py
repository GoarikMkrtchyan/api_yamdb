from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, SignUpSerializer, TokenSerializer
from .models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .utils import send_confirmation_code
from rest_framework.permissions import BasePermission
from .permissions import IsAdminOrSelf, IsAdminOrReadOnly


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        if request.user != self.get_object() and not request.user.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        partial = kwargs.pop('partial', True)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class SignUpViewSet(APIView):
    """ViewSet для регистрации пользователя."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            user, created = User.objects.get_or_create(username=username, email=email)
            if created:
                send_confirmation_code(user)
                return Response({'email': email, 'username': username}, status=status.HTTP_200_OK)
            return Response({'email': email, 'username': username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenViewSet(APIView):
    """ViewSet для получения токена."""
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.is_valid(raise_exception=True)

            username = serializer.validated_data['username']
            confirmation_code = serializer.validated_data['confirmation_code']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "Invalid username"}, status=400)

            if user.confirmation_code != confirmation_code < timezone.now():
                return Response({"error": "Invalid or expired confirmation code"},
                                status=400)

            token = str(RefreshToken.for_user(user))
            return Response({"token": token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
