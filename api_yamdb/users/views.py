from django.utils import timezone
from rest_framework import status, viewsets, filters
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import User
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer
from .utils import send_confirmation_code


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)

    def get_object(self):
        if 'username' in self.kwargs:
            username = self.kwargs['username']
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise NotFound(detail="User not found")
            if not self.request.user.is_admin and user != self.request.user:
                raise NotFound(detail="User not found")
            return user
        return self.request.user

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed('PUT')

        if request.method == 'PATCH':
            user_to_update = self.get_object()
            if request.user.is_admin or request.user == user_to_update:
                partial = kwargs.pop('partial', True)
                serializer = self.get_serializer(user_to_update, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
            return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_admin:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class SignUpViewSet(APIView):
    """ViewSet для регистрации пользователя."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']

            if username.lower() == 'me':
                return Response(
                    {'username': 'This username is reserved.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user, created = User.objects.get_or_create(
                username=username, email=email)
            if created:
                send_confirmation_code(user)
                return Response({'email': email, 'username': username},
                                status=status.HTTP_200_OK)
            else:
                send_confirmation_code(user)
                return Response({'email': email, 'username': username,
                                 'info': 'Confirmation code resent.'},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenViewSet(APIView):
    """ViewSet для получения токена."""
    def post(self, request):
        serializer = TokenSerializer(data=request.data)

        if not request.data:
            return Response(
                {"error": "No data provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            username = serializer.validated_data['username']
            confirmation_code = serializer.validated_data['confirmation_code']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "Invalid username"}, status=400)

            if user.confirmation_code != confirmation_code or timezone.now() > user.confirmation_code_expiry:
                return Response({"error": "Invalid or expired conf. code"},
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
        data = request.data.copy()
        data.pop('role', None)
        serializer = UserSerializer(request.user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)