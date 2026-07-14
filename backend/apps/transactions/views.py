from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDay, TruncMonth
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import datetime, timedelta
from apps.transactions.models import Transaction
from apps.transactions.serializers import (
    TransactionSerializer,
    TransactionCreateSerializer,
    TransactionUpdateSerializer,
    TransactionBulkSerializer,
    SMSParseSerializer,
)
from apps.transactions.services.sms_parser import parse_sms
from apps.transactions.services.category_suggester import suggest_category


class TransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD для транзакций.

    list: GET /api/v1/transactions/
    create: POST /api/v1/transactions/
    retrieve: GET /api/v1/transactions/{id}/
    update: PUT /api/v1/transactions/{id}/
    destroy: DELETE /api/v1/transactions/{id}/
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'category', 'source']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user).select_related(
            'category'
        )
        
        # Фильтрация по датам из query параметров
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TransactionUpdateSerializer
        return self.serializer_class

    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        """
        Массовое создание транзакций (для SMS).
        POST /api/v1/transactions/bulk/
        """
        serializer = TransactionBulkSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        transactions = serializer.save()
        return Response(TransactionSerializer(transactions, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def sms_parse(self, request):
        """
        Парсинг SMS и создание транзакции.
        POST /api/v1/transactions/sms-parse/
        
        Body:
        {
            "sms_text": "текст SMS",
            "bank_phone": "+79000000900" (опционально)
        }
        """
        serializer = SMSParseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sms_text = serializer.validated_data['sms_text']
        bank_phone = serializer.validated_data.get('bank_phone', '')

        # Парсим SMS
        parsed_data = parse_sms(sms_text, bank_phone)

        if not parsed_data:
            return Response(
                {'error': 'Не удалось распознать транзакцию в SMS'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Автоматически находим категорию
        category = suggest_category(parsed_data['description'], parsed_data['type'])

        # Создаём транзакцию
        transaction = Transaction.objects.create(
            user=request.user,
            amount=parsed_data['amount'],
            description=parsed_data['description'],
            type=parsed_data['type'],
            date=parsed_data['date'],
            category=category,
            source='sms',
            is_ai_parsed=bool(category)
        )

        return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def stats_by_category(self, request):
        """
        Статистика по категориям за период.
        GET /api/v1/transactions/stats/by-category/?start_date=2024-01-01&end_date=2024-01-31
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        transactions = Transaction.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )

        # Группировка по категориям
        stats = transactions.filter(type='expense').values(
            'category__name', 'category__color'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        total_expenses = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
        total_income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0

        result = []
        for item in stats:
            percentage = (item['total'] / total_expenses * 100) if total_expenses > 0 else 0
            result.append({
                'category': item['category__name'] or 'Без категории',
                'color': item['category__color'] or '#CCCCCC',
                'amount': float(item['total']),
                'count': item['count'],
                'percentage': round(percentage, 1)
            })

        return Response({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
            },
            'total_expenses': float(total_expenses),
            'total_income': float(total_income),
            'balance': float(total_income - total_expenses),
            'by_category': result
        })

    @action(detail=False, methods=['get'])
    def monthly_stats(self, request):
        """
        Месячная статистика.
        GET /api/v1/transactions/stats/monthly/?months=6
        """
        months = int(request.query_params.get('months', 6))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)

        transactions = Transaction.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )

        # Группировка по месяцам
        monthly = transactions.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            expenses=Sum('amount', filter=Q(type='expense')),
            income=Sum('amount', filter=Q(type='income'))
        ).order_by('month')

        result = []
        for item in monthly:
            result.append({
                'month': item['month'].strftime('%Y-%m'),
                'expenses': float(item['expenses'] or 0),
                'income': float(item['income'] or 0),
                'balance': float((item['income'] or 0) - (item['expenses'] or 0))
            })

        return Response({
            'period_months': months,
            'monthly_data': result
        })

    @action(detail=False, methods=['get'])
    def daily_stats(self, request):
        """
        Дневная статистика.
        GET /api/v1/transactions/stats/daily/?days=30
        """
        days = int(request.query_params.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = Transaction.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )

        # Группировка по дням
        daily = transactions.annotate(
            day=TruncDay('date')
        ).values('day').annotate(
            expenses=Sum('amount', filter=Q(type='expense')),
            income=Sum('amount', filter=Q(type='income'))
        ).order_by('day')

        result = [
            {
                'date': item['day'].strftime('%Y-%m-%d'),
                'expenses': float(item['expenses'] or 0),
                'income': float(item['income'] or 0)
            }
            for item in daily
        ]

        return Response({'daily_data': result})
