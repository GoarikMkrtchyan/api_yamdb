from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, SignUpSerializer, TokenSerializer
from .models import User
from .permissions import IsAdmin
from .utils import send_confirmation_code


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    def get_object(self):
        if self.action == 'me':
            return self.request.user
        return super().get_object()

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role, partial=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class SignUpViewSet(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']

            # Проверка зарезервированного имени
            if username.lower() == 'me':
                return Response(
                    {'username': 'This username is reserved.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user, created = User.objects.get_or_create(
                username=username, email=email)

            if created:
                # Если пользователь был создан, отправляем код подтверждения
                send_confirmation_code(user)
                response_data = {'email': email, 'username': username}
                status_code = status.HTTP_200_OK
            else:
                # Если пользователь уже существует, возвращаем статус 200
                response_data = {'email': email, 'username': username,
                                 'info': 'Confirmation code resent.'}
                status_code = status.HTTP_200_OK

            return Response(response_data, status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenViewSet(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            confirmation_code = serializer.validated_data['confirmation_code']

            user = get_object_or_404(User, username=username)

            if user.confirmation_code != confirmation_code or (
                timezone.now() > user.confirmation_code_expiry
            ):
                return Response(
                    {"error": "Invalid or expired confirmation code"},
                    status=status.HTTP_400_BAD_REQUEST)

            token = str(RefreshToken.for_user(user))
            return Response({"token": token})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
