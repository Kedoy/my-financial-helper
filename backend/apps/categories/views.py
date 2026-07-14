from django.db import models
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from apps.categories.models import Category
from apps.categories.serializers import (
    CategorySerializer,
    CategoryCreateSerializer,
    CategoryUpdateSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD для категорий.

    list: GET /api/v1/categories/
    create: POST /api/v1/categories/
    retrieve: GET /api/v1/categories/{id}/
    update: PUT /api/v1/categories/{id}/
    destroy: DELETE /api/v1/categories/{id}/
    """
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'is_system']

    def get_permissions(self):
        """
        Разрешаем доступ к list и system без аутентификации.
        """
        if self.action in ['list', 'system', 'my']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Возвращаем системные категории + категории пользователя.
        """
        user = self.request.user if hasattr(self.request, 'user') else None
        
        if user and user.is_authenticated:
            # Авторизованный пользователь: системные + свои
            return Category.objects.filter(
                models.Q(is_system=True) | models.Q(user=user)
            ).select_related('user').distinct()
        else:
            # Неавторизованный: только системные
            return Category.objects.filter(
                is_system=True
            ).select_related('user').distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return CategoryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CategoryUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_system:
            return Response(
                {'error': 'Нельзя удалить системную категорию'},
                status=status.HTTP_403_FORBIDDEN
            )
        # Нельзя удалять категории других пользователей
        if instance.user and instance.user != request.user:
            return Response(
                {'error': 'Нельзя удалить категорию другого пользователя'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def system(self, request):
        """
        Получить только системные категории.
        GET /api/v1/categories/system/
        """
        categories = Category.objects.filter(is_system=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my(self, request):
        """
        Получить только пользовательские категории.
        GET /api/v1/categories/my/
        """
        categories = Category.objects.filter(user=request.user)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
