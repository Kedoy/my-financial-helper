"""
LSTM модель для прогнозирования расходов.
Для сравнения с Prophet в научных целях.

Архитектура:
    Input (seq_length) → LSTM(50) → Dropout(0.2) → Dense(1)
"""
import numpy as np
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from apps.transactions.models import Transaction
from typing import Dict, List, Any, Optional


class LSTMForecastService:
    """
    LSTM модель для прогнозирования временных рядов.
    
    Внимание: Требует больше данных для обучения (минимум 60-90 дней).
    На малых данных может показывать худшие результаты чем Prophet.
    """
    
    def __init__(self):
        self.model = None
        self.seq_length = 10  # Длина последовательности для LSTM
        self.scaler = None
    
    def _prepare_data(self, user_id: int) -> Optional[np.ndarray]:
        """
        Подготовка данных для LSTM.
        
        Returns:
            Массив значений расходов по дням
        """
        transactions = Transaction.objects.filter(
            user_id=user_id,
            type='expense'
        ).extra(
            select={'date_only': 'DATE(date)'}
        ).values('date_only').annotate(
            total=Sum('amount')
        ).order_by('date_only')
        
        if transactions.count() < self.seq_length + 5:
            return None
        
        # Преобразуем в массив
        values = [float(item['total']) for item in transactions]
        return np.array(values, dtype=np.float32)
    
    def _create_sequences(self, data: np.ndarray) -> tuple:
        """
        Создание последовательностей для LSTM.
        
        Args:
            data: Временной ряд
            
        Returns:
            X: последовательности входа
            y: целевые значения
        """
        X, y = [], []
        
        for i in range(len(data) - self.seq_length):
            X.append(data[i:i + self.seq_length])
            y.append(data[i + self.seq_length])
        
        return np.array(X), np.array(y)
    
    def _build_model(self, input_shape: int) -> Any:
        """
        Построение LSTM модели.
        
        Архитектура:
            Input → LSTM(50) → Dropout(0.2) → Dense(1)
        """
        try:
            from tensorflow import keras
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from tensorflow.keras.optimizers import Adam
        except ImportError:
            print("[LSTMForecast] TensorFlow not installed. Install with: pip install tensorflow")
            return None
        
        model = Sequential([
            LSTM(50, activation='relu', input_shape=(input_shape, 1)),
            Dropout(0.2),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _normalize(self, data: np.ndarray) -> np.ndarray:
        """Нормализация данных."""
        if len(data) == 0:
            return data
        
        min_val = data.min()
        max_val = data.max()
        
        if max_val - min_val == 0:
            return np.zeros_like(data)
        
        return (data - min_val) / (max_val - min_val), min_val, max_val
    
    def _denormalize(self, data: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
        """Обратная нормализация."""
        return data * (max_val - min_val) + min_val
    
    def forecast_expenses(
        self,
        user_id: int,
        forecast_days: int = 30,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Основной метод прогнозирования.
        
        Args:
            user_id: ID пользователя
            forecast_days: Дней для прогноза
            use_cache: Использовать ли кэш
            
        Returns:
            Словарь с результатами прогноза
        """
        try:
            from tensorflow import keras
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
        except ImportError:
            return {
                'success': False,
                'error': 'TensorFlow не установлен. Установите: pip install tensorflow',
                'model_type': 'LSTM'
            }
        
        # Подготовка данных
        data = self._prepare_data(user_id)
        
        if data is None:
            return {
                'success': False,
                'error': f'Недостаточно данных для LSTM. Минимум {self.seq_length + 5} дней.',
                'model_type': 'LSTM'
            }
        
        # Нормализация
        data_normalized, min_val, max_val = self._normalize(data)
        
        # Создание последовательностей
        X, y = self._create_sequences(data_normalized)
        
        if len(X) < 10:
            return {
                'success': False,
                'error': 'Недостаточно последовательностей для обучения LSTM',
                'model_type': 'LSTM'
            }
        
        # Reshape для LSTM [samples, time steps, features]
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        # Построение модели
        model = self._build_model(self.seq_length)
        
        if model is None:
            return {
                'success': False,
                'error': 'Не удалось создать модель LSTM',
                'model_type': 'LSTM'
            }
        
        # Обучение
        print(f'[LSTMForecast] Training on {len(X)} samples...')
        history = model.fit(
            X, y,
            epochs=50,
            batch_size=16,
            validation_split=0.2,
            verbose=0
        )
        
        # Генерация прогноза
        forecast = self._generate_forecast(
            model=model,
            last_sequence=data_normalized[-self.seq_length:],
            forecast_days=forecast_days,
            min_val=min_val,
            max_val=max_val
        )
        
        # Обработка результатов
        return self._process_results(forecast, data, history)
    
    def _generate_forecast(
        self,
        model: Any,
        last_sequence: np.ndarray,
        forecast_days: int,
        min_val: float,
        max_val: float
    ) -> List[float]:
        """Генерация прогноза на N дней."""
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(forecast_days):
            # Предсказание
            pred_input = current_sequence.reshape(1, self.seq_length, 1)
            pred = model.predict(pred_input, verbose=0)[0, 0]
            
            # Денормализация
            pred_denorm = self._denormalize(np.array([pred]), min_val, max_val)[0]
            predictions.append(float(pred_denorm))
            
            # Обновление последовательности
            current_sequence = np.append(current_sequence[1:], pred)
        
        return predictions
    
    def _process_results(
        self,
        forecast: List[float],
        historical_data: np.ndarray,
        history: Any
    ) -> Dict[str, Any]:
        """Обработка результатов прогноза."""
        import numpy as np
        
        # Метрики обучения
        train_loss = float(history.history['loss'][-1])
        val_loss = float(history.history['val_loss'][-1]) if 'val_loss' in history.history else None
        
        # Статистика прогноза
        forecast_arr = np.array(forecast)
        
        # Доверительный интервал (упрощённо ±15%)
        std_dev = float(np.std(historical_data))
        lower_bound = forecast_arr * 0.85
        upper_bound = forecast_arr * 1.15
        
        # Определение тренда
        trend = self._detect_trend(forecast)
        
        # Дневные прогнозы
        today = timezone.now().date()
        daily_forecasts = []
        for i, pred in enumerate(forecast):
            date = today + timedelta(days=i + 1)
            daily_forecasts.append({
                'date': date.isoformat(),
                'predicted': round(pred, 2),
                'lower_bound': round(lower_bound[i], 2),
                'upper_bound': round(upper_bound[i], 2),
            })
        
        return {
            'success': True,
            'model_type': 'LSTM',
            'forecast_type': 'daily',
            'period_days': len(forecast),
            'summary': {
                'total_predicted': round(float(forecast_arr.sum()), 2),
                'average_daily': round(float(forecast_arr.mean()), 2),
                'lower_bound': round(float(lower_bound.min()), 2),
                'upper_bound': round(float(upper_bound.max()), 2),
                'confidence_level': 85.0,  # LSTM менее уверен
            },
            'trend': trend,
            'daily_forecasts': daily_forecasts,
            'model_info': {
                'architecture': 'LSTM(50) → Dropout(0.2) → Dense(1)',
                'training_samples': len(historical_data),
                'epochs': 50,
                'train_loss': round(train_loss, 6),
                'val_loss': round(val_loss, 6) if val_loss else None,
                'model_version': 'tensorflow-lstm-1.0',
                'generated_at': timezone.now().isoformat(),
            }
        }
    
    def _detect_trend(self, forecast: List[float]) -> Dict[str, Any]:
        """Определение тренда."""
        import numpy as np
        
        if len(forecast) < 2:
            return {'direction': 'stable', 'change_percent': 0}
        
        forecast_arr = np.array(forecast)
        mid = len(forecast) // 2
        
        first_half = forecast_arr[:mid].mean()
        second_half = forecast_arr[mid:].mean()
        
        if first_half == 0:
            change_percent = 0
        else:
            change_percent = ((second_half - first_half) / first_half) * 100
        
        if change_percent > 5:
            direction = 'increasing'
        elif change_percent < -5:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'change_percent': round(change_percent, 2),
            'first_half_avg': round(float(first_half), 2),
            'second_half_avg': round(float(second_half), 2)
        }


# Singleton
lstm_forecast_service = LSTMForecastService()
