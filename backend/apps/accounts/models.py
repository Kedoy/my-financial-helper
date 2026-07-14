from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Расширенная модель пользователя.
    Email используется как основной идентификатор для входа.
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class Profile(models.Model):
    """
    Расширенный профиль пользователя.
    Создается автоматически при регистрации пользователя.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True,
        help_text='Аватар пользователя'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text='Краткая информация о себе',
        max_length=500
    )
    currency = models.CharField(max_length=3, default='RUB', help_text='Код валюты (RUB, USD, EUR)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        ordering = ['-created_at']

    def __str__(self):
        return f'Профиль {self.user.email}'
