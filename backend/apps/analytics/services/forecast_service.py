"""
Сервис прогнозирования расходов на основе Facebook Prophet.
Использует Redis для кэширования моделей и прогнозов.
"""
import json
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, List, Any

import pandas as pd
import redis
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from apps.transactions.models import Transaction


class RedisForecastCache:
    """
    Менеджер кэширования прогнозов в Redis.
    Кэширует:
    1. Готовые прогнозы
    2. Обученные модели (сериализованные)
    """
    
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Подключение к Redis."""
        try:
            redis_config = getattr(settings, 'CACHES', {}).get('redis', {})
            location = redis_config.get('LOCATION', 'localhost:6379')
            
            # Парсим LOCATION правильно (может быть redis://host:port/db или host:port)
            if location.startswith('redis://'):
                # Формат: redis://host:port/db
                location = location.replace('redis://', '')
                parts = location.split('/')
                db = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                host_port = parts[0].split(':')
            else:
                # Формат: host:port
                host_port = location.split(':')
                db = redis_config.get('OPTIONS', {}).get('db', 0)
            
            host = host_port[0] if host_port else 'localhost'
            port = int(host_port[1]) if len(host_port) > 1 else 6379
            
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=redis_config.get('OPTIONS', {}).get('password'),
                decode_responses=True,
                socket_connect_timeout=5,
            )
            # Проверка подключения
            self.redis_client.ping()
            print(f'[RedisForecast] Connected to Redis at {host}:{port} (db={db})')
        except Exception as e:
            print(f'[RedisForecast] Redis connection failed: {e}. Falling back to DB-only mode.')
            self.redis_client = None
    
    def _generate_cache_key(
        self,
        user_id: int,
        forecast_type: str,
        period_days: int,
        category_id: Optional[int] = None
    ) -> str:
        """Генерация уникального ключа кэша."""
        category_part = f'cat:{category_id}' if category_id else 'all'
        key_string = f'forecast:user:{user_id}:type:{forecast_type}:days:{period_days}:{category_part}'
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_forecast(
        self,
        user_id: int,
        forecast_type: str,
        period_days: int,
        category_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Получение прогноза из кэша."""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f'forecast:{self._generate_cache_key(user_id, forecast_type, period_days)}'
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                print(f'[RedisForecast] Cache hit for user {user_id}')
                return json.loads(cached_data)
        except Exception as e:
            print(f'[RedisForecast] Cache get error: {e}')
        return None
    
    def set_forecast(
        self,
        user_id: int,
        forecast_type: str,
        period_days: int,
        forecast_data: Dict,
        category_id: Optional[int] = None,
        ttl: int = 3600
    ) -> bool:
        """Сохранение прогноза в кэш."""
        if not self.redis_client:
            return False
        
        try:
            cache_key = f'forecast:{self._generate_cache_key(user_id, forecast_type, period_days)}'
            self.redis_client.setex(
                cache_key,
                ttl,  # Time to live в секундах
                json.dumps(forecast_data, default=str)
            )
            print(f'[RedisForecast] Cache set for user {user_id}, TTL: {ttl}s')
            return True
        except Exception as e:
            print(f'[RedisForecast] Cache set error: {e}')
            return False
    
    def invalidate_forecast(self, user_id: int, forecast_type: str, period_days: int) -> bool:
        """Инвалидация кэша прогноза."""
        if not self.redis_client:
            return False
        
        try:
            cache_key = f'forecast:{self._generate_cache_key(user_id, forecast_type, period_days)}'
            self.redis_client.delete(cache_key)
            print(f'[RedisForecast] Cache invalidated for user {user_id}')
            return True
        except Exception as e:
            print(f'[RedisForecast] Cache invalidate error: {e}')
            return False
    
    def is_available(self) -> bool:
        """Проверка доступности Redis."""
        return self.redis_client is not None


class ProphetForecastService:
    """
    Сервис прогнозирования расходов с использованием Prophet.
    
    Prophet особенно хорош для:
    - Временных рядов с сезонностью (недельной, месячной, годовой)
    - Данных с выбросами и пропусками
    - Прогнозов с доверительными интервалами
    """
    
    def __init__(self):
        self.cache = RedisForecastCache()
        self._model = None
    
    def _prepare_training_data(
        self,
        user_id: int,
        category_id: Optional[int] = None,
        min_data_points: int = 30
    ) -> Optional[List[Dict]]:
        """
        Подготовка данных для обучения модели.
        
        Args:
            user_id: ID пользователя
            category_id: ID категории (опционально, если None - все расходы)
            min_data_points: Минимальное количество точек данных для обучения
            
        Returns:
            Список словарей с датой и суммой расходов
        """
        # Фильтр по категории
        filters = {
            'user_id': user_id,
            'type': 'expense'
        }
        if category_id:
            filters['category_id'] = category_id
        
        # Получаем все расходы пользователя, сгруппированные по дням
        transactions = Transaction.objects.filter(
            **filters
        ).extra(
            select={'date_only': 'DATE(date)'}
        ).values('date_only').annotate(
            total=Sum('amount')
        ).order_by('date_only')
        
        if transactions.count() < min_data_points:
            print(f'[ProphetForecast] Insufficient data: {transactions.count()} < {min_data_points}')
            return None
        
        # Форматируем данные для Prophet
        # Prophet требует колонки: 'ds' (дата) и 'y' (значение)
        training_data = []
        for item in transactions:
            date_value = item['date_only']
            # date_only может быть строкой или date объектом
            if isinstance(date_value, str):
                from datetime import datetime
                date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
            
            training_data.append({
                'ds': date_value.isoformat(),
                'y': float(item['total'])
            })
        
        print(f'[ProphetForecast] Prepared {len(training_data)} data points for user {user_id}')
        return training_data
    
    def _create_prophet_model(self, training_data: List[Dict]) -> Any:
        """
        Создание и обучение модели Prophet.
        
        Args:
            training_data: Данные для обучения в формате [{'ds': date, 'y': value}, ...]
            
        Returns:
            Обученная модель Prophet
        """
        try:
            from prophet import Prophet
            import pandas as pd
            
            # Конвертируем в DataFrame
            df = pd.DataFrame(training_data)
            df['ds'] = pd.to_datetime(df['ds'])
            
            # Создаём модель с настройками
            model = Prophet(
                daily_seasonality='auto',  # Дневная сезонность
                weekly_seasonality='auto',  # Недельная сезонность
                yearly_seasonality='auto',  # Годовая сезонность
                changepoint_prior_scale=0.05,  # Гибкость тренда
                interval_width=0.95,  # 95% доверительный интервал
                uncertainty_samples=1000,  # Количество сэмплов для uncertainty
            )
            
            # Добавляем регрессоры (можно добавить позже)
            # model.add_country_holidays(country_name='RU')  # Российские праздники
            
            # Обучаем модель
            print(f'[ProphetForecast] Training model on {len(df)} samples...')
            model.fit(df)
            
            return model
            
        except ImportError as e:
            print(f'[ProphetForecast] Prophet not installed: {e}')
            raise
        except Exception as e:
            print(f'[ProphetForecast] Model creation error: {e}')
            raise
    
    def _generate_forecast(self, model: Any, periods: int) -> pd.DataFrame:
        """
        Генерация прогноза на N периодов.
        
        Args:
            model: Обученная модель Prophet
            periods: Количество дней для прогноза
            
        Returns:
            DataFrame с прогнозами
        """
        # Создаём future dataframe
        future = model.make_future_dataframe(periods=periods, freq='D')
        
        # Делаем прогноз
        forecast = model.predict(future)
        
        return forecast
    
    def forecast_expenses(
        self,
        user_id: int,
        forecast_type: str = 'daily',
        period_days: int = 30,
        category_id: Optional[int] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Основной метод прогнозирования расходов.
        
        Args:
            user_id: ID пользователя
            forecast_type: Тип прогноза ('daily', 'weekly', 'monthly')
            period_days: Период прогноза в днях
            category_id: ID категории (опционально, если None - все расходы)
            use_cache: Использовать ли кэш Redis
            
        Returns:
            Словарь с результатами прогноза
        """
        # Проверяем кэш
        if use_cache:
            cached_forecast = self.cache.get_forecast(
                user_id,
                forecast_type,
                period_days,
                category_id
            )
            if cached_forecast:
                return cached_forecast
        
        # Подготовка данных
        training_data = self._prepare_training_data(
            user_id=user_id,
            category_id=category_id,
            min_data_points=30
        )
        
        if not training_data:
            return {
                'success': False,
                'error': 'Недостаточно данных для прогноза. Минимум 30 транзакций.',
                'min_data_points': 30,
                'current_data_points': 0
            }
        
        try:
            # Обучение модели
            model = self._create_prophet_model(training_data)
            
            # Генерация прогноза
            forecast_df = self._generate_forecast(model, period_days)
            
            # Обработка результатов
            result = self._process_forecast_results(
                model=model,
                forecast_df=forecast_df,
                user_id=user_id,
                forecast_type=forecast_type,
                period_days=period_days,
                category_id=category_id,
                training_data_points=len(training_data)
            )
            
            # Сохраняем в кэш
            if use_cache:
                ttl = self._get_cache_ttl(forecast_type)
                self.cache.set_forecast(
                    user_id,
                    forecast_type,
                    period_days,
                    result,
                    category_id=category_id,
                    ttl=ttl
                )
            
            return result
            
        except Exception as e:
            print(f'[ProphetForecast] Forecast error: {e}')
            return {
                'success': False,
                'error': f'Ошибка прогнозирования: {str(e)}'
            }
    
    def _process_forecast_results(
        self,
        model: Any,
        forecast_df: pd.DataFrame,
        user_id: int,
        forecast_type: str,
        period_days: int,
        category_id: Optional[int],
        training_data_points: int
    ) -> Dict[str, Any]:
        """
        Обработка результатов прогноза.
        
        Returns:
            Словарь с прогнозом и метаданными
        """
        import pandas as pd
        
        # Берём только будущие даты (прогноз)
        today = timezone.now().date()
        forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])
        future_forecast = forecast_df[forecast_df['ds'].dt.date > today].head(period_days)
        
        if len(future_forecast) == 0:
            return {
                'success': False,
                'error': 'Нет будущих дат для прогноза'
            }
        
        # Суммарный прогноз
        total_predicted = float(future_forecast['yhat'].sum())
        avg_lower = float(future_forecast['yhat_lower'].mean())
        avg_upper = float(future_forecast['yhat_upper'].mean())
        
        # Детализация по дням
        daily_forecasts = []
        for _, row in future_forecast.iterrows():
            daily_forecasts.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted': round(float(row['yhat']), 2),
                'lower_bound': round(float(row['yhat_lower']), 2),
                'upper_bound': round(float(row['yhat_upper']), 2),
            })
        
        # Определяем тренд
        trend = self._detect_trend(future_forecast['yhat'].tolist())
        
        result = {
            'success': True,
            'forecast_type': forecast_type,
            'period_days': period_days,
            'summary': {
                'total_predicted': round(total_predicted, 2),
                'average_daily': round(total_predicted / len(future_forecast), 2),
                'lower_bound': round(min(future_forecast['yhat_lower']), 2),
                'upper_bound': round(max(future_forecast['yhat_upper']), 2),
                'confidence_level': 95.0,
            },
            'trend': trend,
            'daily_forecasts': daily_forecasts,
            'model_info': {
                'training_data_points': training_data_points,
                'model_version': 'prophet-1.1.5',
                'generated_at': timezone.now().isoformat(),
                'expires_at': (timezone.now() + timedelta(hours=1)).isoformat(),
            }
        }
        
        return result
    
    def _detect_trend(self, values: List[float]) -> Dict[str, Any]:
        """
        Определение тренда расходов.
        
        Returns:
            Информация о тренде
        """
        if len(values) < 2:
            return {'direction': 'stable', 'change_percent': 0}
        
        # Сравниваем первую и вторую половину прогноза
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid
        second_half_avg = sum(values[mid:]) / (len(values) - mid)
        
        if first_half_avg == 0:
            change_percent = 0
        else:
            change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if change_percent > 5:
            direction = 'increasing'
        elif change_percent < -5:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'change_percent': round(change_percent, 2),
            'first_half_avg': round(first_half_avg, 2),
            'second_half_avg': round(second_half_avg, 2)
        }
    
    def _get_cache_ttl(self, forecast_type: str) -> int:
        """
        Определение TTL кэша в зависимости от типа прогноза.
        
        Returns:
            TTL в секундах
        """
        ttl_map = {
            'daily': 3600,      # 1 час
            'weekly': 7200,     # 2 часа
            'monthly': 14400,   # 4 часа
        }
        return ttl_map.get(forecast_type, 3600)
    
    def invalidate_user_forecasts(self, user_id: int) -> bool:
        """
        Инвалидация всех прогнозов пользователя.
        Вызывать при добавлении/изменении транзакций.
        """
        success = True
        for forecast_type in ['daily', 'weekly', 'monthly']:
            for period in [7, 14, 30, 60, 90]:
                if not self.cache.invalidate_forecast(user_id, forecast_type, period):
                    success = False
        return success


# Singleton instance
forecast_service = ProphetForecastService()
