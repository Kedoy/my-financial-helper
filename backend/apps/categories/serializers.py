from rest_framework import serializers
from apps.categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer для категории."""
    transactions_count = serializers.IntegerField(source='transactions.count', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'type', 'icon', 'color', 'user',
            'is_system', 'transactions_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_system', 'created_at', 'updated_at']


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer для создания категории."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon', 'color']

    def create(self, validated_data):
        # Пользовательские категории не могут быть системными
        validated_data['user'] = self.context['request'].user
        validated_data['is_system'] = False
        return super().create(validated_data)


class CategoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer для обновления категории."""

    class Meta:
        model = Category
        fields = ['name', 'icon', 'color']

    def update(self, instance, validated_data):
        # Нельзя изменять системные категории
        if instance.is_system:
            raise serializers.ValidationError('Нельзя изменять системную категорию')
        # Нельзя сделать категорию системной
        if validated_data.get('is_system'):
            raise serializers.ValidationError('Нельзя сделать категорию системной')
        return super().update(instance, validated_data)
