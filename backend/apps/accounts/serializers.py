from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer для профиля пользователя."""
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'avatar', 'avatar_url', 'bio', 'currency', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer для обновления профиля пользователя."""

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'currency']


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'profile', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_profile(self, obj):
        request = self.context.get('request')
        profile = getattr(obj, 'profile', None)
        if profile:
            return ProfileSerializer(profile, context={'request': request}).data
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer для регистрации пользователя."""
    password = serializers.CharField(write_only=True, min_length=8, label='Пароль')
    password_confirm = serializers.CharField(write_only=True, min_length=8, label='Подтверждение пароля')

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        
        # Проверка на существующий email
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Пользователь с таким email уже существует'})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', validated_data['email'].split('@')[0]),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        Profile.objects.create(user=user)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer для обновления профиля пользователя."""
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        read_only_fields = ['email']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer для токенов с данными пользователя.
    Позволяет использовать email вместо username для входа.
    """

    def validate(self, attrs):
        email = attrs.get('username', '')

        if 'email' in attrs:
            email = attrs['email']

        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError('Неверный email или пароль')
        
        if not user.check_password(attrs.get('password')):
            raise ValidationError('Неверный email или пароль')
        
        if not user.is_active:
            raise ValidationError('Аккаунт не активен')

        # Получаем токены
        refresh = self.get_token(user)

        data = {
            'access_token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer для запроса сброса пароля."""
    email = serializers.EmailField(label='Email', required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer для подтверждения сброса пароля."""
    token = serializers.CharField(label='Токен', write_only=True)
    password = serializers.CharField(min_length=8, label='Новый пароль', write_only=True)
    password_confirm = serializers.CharField(min_length=8, label='Подтверждение пароля', write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        return attrs
