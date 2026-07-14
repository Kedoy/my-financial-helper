from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.cache import cache
from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
)
from .models import Profile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    POST /api/v1/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    Вход пользователя с установкой Refresh Token в Cookie.
    POST /api/v1/auth/login/

    Body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    или
    {
        "username": "user@example.com",
        "password": "password123"
    }
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Используем наш кастомный serializer напрямую
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Получаем данные из serializer
        data = serializer.validated_data
        
        # Формируем ответ
        response = Response({
            'access_token': data['access_token'],
            'user': data['user']
        })

        # Устанавливаем Refresh Token в HttpOnly Cookie
        refresh_token = data.get('refresh')
        if refresh_token:
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=settings.DEBUG is False,  # HTTPS только в продакшене
                samesite='Lax',
                max_age=7 * 24 * 60 * 60,  # 7 дней
                path='/api/v1/auth/refresh/'
            )

        return response


class LogoutView(APIView):
    """
    Выход пользователя с очисткой Cookie.
    POST /api/v1/auth/logout/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({'message': 'Выход выполнен успешно'})
        response.delete_cookie('refresh_token')
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Обновление токена из Cookie.
    POST /api/v1/auth/refresh/
    """

    def post(self, request, *args, **kwargs):
        # Берём refresh token из Cookie
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token не найден'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)

        # Обновляем Cookie с новым refresh token
        if response.status_code == 200:
            new_refresh_token = response.data.get('refresh')
            if new_refresh_token:
                response.set_cookie(
                    key='refresh_token',
                    value=new_refresh_token,
                    httponly=True,
                    secure=settings.DEBUG is False,
                    samesite='Lax',
                    max_age=7 * 24 * 60 * 60,
                    path='/api/v1/auth/refresh/'
                )
                response.data.pop('refresh', None)

        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Просмотр и обновление профиля пользователя.
    GET/PUT /api/v1/auth/me/
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Детальное управление профилем (avatar, bio, currency).
    GET/PUT /api/v1/auth/profile/
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Возвращаем обновленные данные с правильным контекстом
        instance.refresh_from_db()
        return Response(ProfileSerializer(instance, context={'request': request}).data)

    def perform_update(self, serializer):
        # Сохраняем профиль с обработкой изображения
        serializer.save()


class PasswordResetRequestView(APIView):
    """
    Запрос на сброс пароля.
    POST /api/v1/auth/password/reset/
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            # Генерируем токен
            token = get_random_string(32)
            cache.set(f'password_reset_{token}', user.id, timeout=3600)  # 1 час

            # Отправляем email
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}/"
            send_mail(
                'Сброс пароля Ks Financial App',
                f'Перейдите по ссылке для сброса пароля: {reset_link}\n\nСсылка действительна в течение 1 часа.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )

        # Всегда возвращаем успех для безопасности (не раскрываем существование email)
        return Response(
            {'message': 'Если пользователь существует, письмо с инструкциями отправлено'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    Подтверждение сброса пароля.
    POST /api/v1/auth/password/reset/confirm/
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        user_id = cache.get(f'password_reset_{token}')

        if not user_id:
            return Response(
                {'error': 'Токен недействителен или истёк'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.get(id=user_id)
        user.set_password(serializer.validated_data['password'])
        user.save()

        cache.delete(f'password_reset_{token}')

        return Response({'message': 'Пароль успешно изменён'})
