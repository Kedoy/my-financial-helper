"""
Тесты для системы прогнозирования расходов.
"""
import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.transactions.models import Transaction
from apps.categories.models import Category


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='test_forecast_user',
        email='test@forecast.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def category():
    return Category.objects.create(
        name='Тестовая категория',
        color='#FF5733',
        icon='shopping',
        type='expense'
    )


@pytest.fixture
def transactions_with_history(user, category):
    """
    Создаёт тестовые транзакции за последние 60 дней.
    Для работы Prophet нужно минимум 30 точек данных.
    """
    transactions = []
    today = timezone.now()
    
    # Создаём транзакции за последние 60 дней
    for i in range(60):
        date = today - timedelta(days=i)
        # Расходы с некоторой случайностью и трендом
        amount = Decimal('1000') + Decimal(i * 10)  # Небольшой растущий тренд
        
        transactions.append(Transaction.objects.create(
            user=user,
            category=category,
            amount=amount,
            description=f'Тестовая транзакция {i}',
            type='expense',
            source='manual',
            date=date
        ))
    
    return transactions


@pytest.mark.django_db
class TestExpenseForecastView:
    """Тесты для API прогноза расходов."""
    
    def test_forecast_requires_auth(self, api_client):
        """Прогноз доступен только авторизованным пользователям."""
        response = api_client.get('/api/v1/analytics/forecast/')
        assert response.status_code == 401
    
    def test_forecast_insufficient_data(self, api_client, user):
        """Тест: недостаточно данных для прогноза."""
        api_client.force_authenticate(user=user)
        
        response = api_client.get('/api/v1/analytics/forecast/?type=daily&period=30')
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'Недостаточно данных' in data.get('error', '')
    
    def test_forecast_with_sufficient_data(
        self, api_client, user, category, transactions_with_history
    ):
        """Тест: прогноз с достаточным количеством данных."""
        api_client.force_authenticate(user=user)
        
        response = api_client.get('/api/v1/analytics/forecast/?type=daily&period=30')
        
        # Проверяем успешный ответ
        data = response.json()
        assert data['success'] is True
        assert 'summary' in data
        assert 'daily_forecasts' in data
        assert 'trend' in data
        
        # Проверяем структуру summary
        summary = data['summary']
        assert 'total_predicted' in summary
        assert 'average_daily' in summary
        assert 'lower_bound' in summary
        assert 'upper_bound' in summary
        assert 'confidence_level' in summary
        
        # Проверяем количество дней прогноза
        assert len(data['daily_forecasts']) <= 30
        
        # Проверяем тренд
        trend = data['trend']
        assert 'direction' in trend
        assert 'change_percent' in trend
    
    def test_forecast_invalid_type(self, api_client, user, transactions_with_history):
        """Тест: неверный тип прогноза."""
        api_client.force_authenticate(user=user)
        
        response = api_client.get('/api/v1/analytics/forecast/?type=invalid&period=30')
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
    
    def test_forecast_invalid_period(self, api_client, user, transactions_with_history):
        """Тест: неверный период прогноза."""
        api_client.force_authenticate(user=user)
        
        response = api_client.get('/api/v1/analytics/forecast/?type=daily&period=999')
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
    
    def test_forecast_summary_endpoint(
        self, api_client, user, category, transactions_with_history
    ):
        """Тест: краткая сводка прогноза."""
        api_client.force_authenticate(user=user)
        
        response = api_client.get('/api/v1/analytics/forecast/summary/')
        
        data = response.json()
        if data.get('success'):
            assert 'forecast_available' in data
            assert 'next_30_days' in data
            assert 'confidence' in data
        else:
            # Если недостаточно данных
            assert data['forecast_available'] is False


@pytest.mark.django_db
class TestForecastService:
    """Тесты для сервиса прогнозирования."""
    
    def test_prepare_training_data(self, user, category, transactions_with_history):
        """Тест: подготовка данных для обучения."""
        from apps.analytics.services.forecast_service import ProphetForecastService
        
        service = ProphetForecastService()
        training_data = service._prepare_training_data(user.id)
        
        assert training_data is not None
        assert len(training_data) >= 30
        assert 'ds' in training_data[0]
        assert 'y' in training_data[0]
    
    def test_trend_detection_increasing(self):
        """Тест: определение растущего тренда."""
        from apps.analytics.services.forecast_service import ProphetForecastService
        
        service = ProphetForecastService()
        
        # Растущие значения
        values = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210]
        trend = service._detect_trend(values)
        
        assert trend['direction'] == 'increasing'
        assert trend['change_percent'] > 0
    
    def test_trend_detection_decreasing(self):
        """Тест: определение падающего тренда."""
        from apps.analytics.services.forecast_service import ProphetForecastService
        
        service = ProphetForecastService()
        
        # Падающие значения
        values = [200, 190, 180, 170, 160, 150, 140, 130, 120, 110, 100, 90]
        trend = service._detect_trend(values)
        
        assert trend['direction'] == 'decreasing'
        assert trend['change_percent'] < 0
    
    def test_trend_detection_stable(self):
        """Тест: определение стабильного тренда."""
        from apps.analytics.services.forecast_service import ProphetForecastService
        
        service = ProphetForecastService()
        
        # Стабильные значения с небольшим шумом
        values = [100, 102, 98, 101, 99, 100, 101, 99, 100, 101, 99, 100]
        trend = service._detect_trend(values)
        
        assert trend['direction'] == 'stable'


@pytest.mark.django_db
class TestForecastCache:
    """Тесты для Redis кэширования."""
    
    def test_cache_service_initialization(self):
        """Тест: инициализация сервиса кэширования."""
        from apps.analytics.services.forecast_service import RedisForecastCache
        
        cache = RedisForecastCache()
        # Сервис должен инициализироваться даже без Redis
        assert cache is not None
    
    def test_cache_set_get_without_redis(self):
        """Тест: кэширование без Redis (fallback)."""
        from apps.analytics.services.forecast_service import RedisForecastCache
        
        cache = RedisForecastCache()
        
        # Без Redis set_forecast должен вернуть False
        result = cache.set_forecast(1, 'daily', 30, {'test': 'data'})
        assert result is False
        
        # get_forecast должен вернуть None
        data = cache.get_forecast(1, 'daily', 30)
        assert data is None


@pytest.mark.django_db
class TestForecastModel:
    """Тесты для модели Forecast."""
    
    def test_forecast_creation(self, user):
        """Тест: создание прогноза."""
        from apps.analytics.models import Forecast
        
        forecast = Forecast.objects.create(
            user=user,
            forecast_type='daily',
            period_days=30,
            predicted_amount=Decimal('30000.00'),
            lower_bound=Decimal('25000.00'),
            upper_bound=Decimal('35000.00'),
            confidence=Decimal('95.00'),
            training_data_points=60,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        assert forecast is not None
        assert str(forecast).startswith('Прогноз для')
        assert forecast.is_actual is True
    
    def test_forecast_detail_creation(self, user):
        """Тест: создание деталей прогноза."""
        from apps.analytics.models import Forecast, ForecastDetail
        
        forecast = Forecast.objects.create(
            user=user,
            forecast_type='daily',
            period_days=7,
            predicted_amount=Decimal('7000.00'),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # Создаём детали прогноза
        for i in range(7):
            date = timezone.now().date() + timedelta(days=i)
            ForecastDetail.objects.create(
                forecast=forecast,
                date=date,
                predicted_value=Decimal('1000.00'),
                lower_bound=Decimal('900.00'),
                upper_bound=Decimal('1100.00')
            )
        
        assert forecast.details.count() == 7
