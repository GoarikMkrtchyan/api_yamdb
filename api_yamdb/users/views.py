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
    permission_classes = [IsAdminOrSelf]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['username']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAdminOrReadOnly]
        elif self.action in ['create']:
            self.permission_classes = [IsAdminOrReadOnly]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAdminOrSelf]
        elif self.action in ['destroy']:
            self.permission_classes = [IsAdminOrReadOnly]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({'detail': 'Not authorized to create users'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({'detail': 'Not authorized to update users'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # Ensure username is in kwargs
        if 'username' in kwargs:
            user = self.get_object()
            if request.user.role != 'admin' and request.user != user:
                return Response({'detail': 'Not authorized to update this user'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({'detail': 'Not authorized to delete users'}, status=status.HTTP_404_NOT_FOUND)
        return super().destroy(request, *args, **kwargs)

    def get_object(self):
        if 'username' in self.kwargs:
            return User.objects.get(username=self.kwargs['username'])
        return super().get_object()


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
        """Возвращает информацию о текущем пользователе."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Частичное обновление данных текущего пользователя."""
        # Удаление поля 'role' из данных запроса, чтобы предотвратить его изменение
        if 'role' in request.data:
            request.data.pop('role')

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Удаление текущего пользователя не разрешено."""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
