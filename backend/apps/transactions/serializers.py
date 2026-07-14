from rest_framework import serializers
from apps.transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer для транзакции."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'category', 'category_name', 'category_color',
            'amount', 'description', 'type', 'source', 'is_ai_parsed',
            'date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'source', 'is_ai_parsed', 'created_at', 'updated_at']


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer для создания транзакции."""

    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'description', 'type', 'date']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['source'] = 'manual'
        return super().create(validated_data)


class TransactionUpdateSerializer(serializers.ModelSerializer):
    """Serializer для обновления транзакции."""

    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'description', 'type', 'date']


class TransactionBulkSerializer(serializers.Serializer):
    """Serializer для массового создания транзакций."""
    transactions = TransactionCreateSerializer(many=True)

    def create(self, validated_data):
        transactions_data = validated_data['transactions']
        user = self.context['request'].user
        created_transactions = []
        
        for tx_data in transactions_data:
            tx_data['user'] = user
            tx_data['source'] = 'sms'
            tx = Transaction.objects.create(**tx_data)
            created_transactions.append(tx)
        
        return created_transactions


class SMSParseSerializer(serializers.Serializer):
    """Serializer для парсинга SMS."""
    sms_text = serializers.CharField(label='Текст SMS')
    bank_phone = serializers.CharField(label='Номер банка', required=False, allow_blank=True)

    def validate_sms_text(self, value):
        if not value.strip():
            raise serializers.ValidationError('Текст SMS не может быть пустым')
        return value.strip()
