"""
XGBoost модель для прогнозирования расходов.
Для сравнительного анализа с Prophet и LSTM.

Преимущества XGBoost:
- Быстрее LSTM
- Лучше интерпретируемость чем у LSTM
- Хорошо работает на средних выборках (50-200 точек)
"""
import numpy as np
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Sum
from apps.transactions.models import Transaction
from typing import Dict, List, Any, Optional


class XGBoostForecastService:
    """
    XGBoost модель для прогнозирования временных рядов.
    
    Использует инженерные признаки:
    - День недели
    - День месяца
    - Месяц
    - Скользящие средние
    - Лаги
    """
    
    def __init__(self):
        self.model = None
        self.lag_days = 7  # Количество лагов
        self.window_sizes = [7, 14, 30]  # Окна для скользящих средних
    
    def _prepare_features(self, user_id: int) -> Optional[Dict]:
        """
        Подготовка данных и признаков для XGBoost.
        """
        transactions = Transaction.objects.filter(
            user_id=user_id,
            type='expense'
        ).extra(
            select={'date_only': 'DATE(date)'}
        ).values('date_only').annotate(
            total=Sum('amount')
        ).order_by('date_only')
        
        if transactions.count() < max(self.window_sizes):
            return None
        
        # Создаём DataFrame с признаками
        import pandas as pd
        
        data = []
        for item in transactions:
            date_str = item['date_only']
            date = datetime.strptime(date_str, '%Y-%m-%d') if isinstance(date_str, str) else date_str
            
            data.append({
                'date': date,
                'amount': float(item['total'])
            })
        
        df = pd.DataFrame(data)
        
        # Временные признаки
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        
        # Лаги
        for i in range(1, self.lag_days + 1):
            df[f'lag_{i}'] = df['amount'].shift(i)
        
        # Скользящие средние
        for window in self.window_sizes:
            df[f'ma_{window}'] = df['amount'].shift(1).rolling(window=window).mean()
        
        # Скользящее стандартное отклонение
        df['std_7'] = df['amount'].shift(1).rolling(window=7).std()
        
        # Тренд (разница с предыдущим днём)
        df['diff_1'] = df['amount'].diff(1)
        
        # Удаляем NaN
        df = df.dropna()
        
        return {
            'df': df,
            'feature_columns': [col for col in df.columns if col not in ['date', 'amount']]
        }
    
    def _build_model(self):
        """Построение XGBoost модели."""
        try:
            import xgboost as xgb
        except ImportError:
            print("[XGBoostForecast] XGBoost not installed. Install with: pip install xgboost")
            return None
        
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            objective='reg:squarederror',
            random_state=42,
            n_jobs=-1
        )
        
        return model
    
    def forecast_expenses(
        self,
        user_id: int,
        forecast_days: int = 30,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Основной метод прогнозирования.
        """
        try:
            import xgboost as xgb
            import pandas as pd
        except ImportError:
            return {
                'success': False,
                'error': 'XGBoost не установлен. Установите: pip install xgboost',
                'model_type': 'XGBoost'
            }
        
        # Подготовка данных
        prepared = self._prepare_features(user_id)
        
        if prepared is None:
            return {
                'success': False,
                'error': f'Недостаточно данных для XGBoost. Минимум {max(self.window_sizes)} дней.',
                'model_type': 'XGBoost'
            }
        
        df = prepared['df']
        feature_cols = prepared['feature_columns']
        
        if len(df) < 20:
            return {
                'success': False,
                'error': 'Недостаточно данных после создания признаков',
                'model_type': 'XGBoost'
            }
        
        # Разделение на признаки и целевую переменную
        X = df[feature_cols].values
        y = df['amount'].values
        
        # Обучение модели
        print(f'[XGBoostForecast] Training on {len(X)} samples...')
        model = self._build_model()
        
        if model is None:
            return {
                'success': False,
                'error': 'Не удалось создать модель XGBoost',
                'model_type': 'XGBoost'
            }
        
        model.fit(X, y)
        
        # Генерация прогноза
        forecast = self._generate_forecast(
            model=model,
            df=df,
            feature_cols=feature_cols,
            forecast_days=forecast_days
        )
        
        # Обработка результатов
        return self._process_results(forecast, df, model, feature_cols)
    
    def _generate_forecast(
        self,
        model: Any,
        df: Any,
        feature_cols: List[str],
        forecast_days: int
    ) -> List[float]:
        """Генерация прогноза на N дней."""
        import pandas as pd
        import numpy as np
        
        predictions = []
        
        # Берём последние данные для инициализации
        last_row = df.iloc[-1].copy()
        last_date = last_row['date']
        
        # История для лагов
        amount_history = df['amount'].tolist()[-self.lag_days:]
        ma_history = {w: df[f'ma_{w}'].iloc[-1] for w in self.window_sizes}
        
        for i in range(forecast_days):
            # Следующая дата
            next_date = last_date + timedelta(days=i + 1)
            
            # Создаём признаки для следующего дня
            features = {
                'day_of_week': next_date.weekday(),
                'day_of_month': next_date.day,
                'month': next_date.month,
                'is_weekend': 1 if next_date.weekday() >= 5 else 0,
                'is_month_start': 1 if next_date.day == 1 else 0,
                'is_month_end': 1 if next_date.day == (next_date.replace(day=28) + timedelta(days=4)).day else 0,
            }
            
            # Лаги
            for j in range(1, self.lag_days + 1):
                if j <= len(amount_history):
                    features[f'lag_{j}'] = amount_history[-j]
                else:
                    features[f'lag_{j}'] = 0
            
            # Скользящие средние (упрощённо)
            for w in self.window_sizes:
                features[f'ma_{w}'] = ma_history.get(w, 0)
            
            # Стандартное отклонение
            features['std_7'] = df['std_7'].iloc[-1] if 'std_7' in df.columns else 0
            
            # Разница
            features['diff_1'] = amount_history[-1] - amount_history[-2] if len(amount_history) >= 2 else 0
            
            # Предсказание
            X_pred = np.array([[features[col] for col in feature_cols]])
            pred = model.predict(X_pred)[0]
            
            # Гарантируем неотрицательность
            pred = max(0, pred)
            predictions.append(float(pred))
            
            # Обновляем историю
            amount_history.append(pred)
            if len(amount_history) > self.lag_days:
                amount_history.pop(0)
        
        return predictions
    
    def _process_results(
        self,
        forecast: List[float],
        df: Any,
        model: Any,
        feature_cols: List[str]
    ) -> Dict[str, Any]:
        """Обработка результатов прогноза."""
        import numpy as np
        
        forecast_arr = np.array(forecast)
        historical = df['amount'].values
        
        # Статистика
        std_dev = float(np.std(historical))
        
        # Доверительный интервал (±12% для XGBoost)
        lower_bound = forecast_arr * 0.88
        upper_bound = forecast_arr * 1.12
        
        # Тренд
        trend = self._detect_trend(forecast)
        
        # Важность признаков
        feature_importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        
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
            'model_type': 'XGBoost',
            'forecast_type': 'daily',
            'period_days': len(forecast),
            'summary': {
                'total_predicted': round(float(forecast_arr.sum()), 2),
                'average_daily': round(float(forecast_arr.mean()), 2),
                'lower_bound': round(float(lower_bound.min()), 2),
                'upper_bound': round(float(upper_bound.max()), 2),
                'confidence_level': 88.0,
            },
            'trend': trend,
            'daily_forecasts': daily_forecasts,
            'feature_importance': {k: round(v, 4) for k, v in top_features},
            'model_info': {
                'architecture': 'XGBoost Regressor (n_estimators=100, max_depth=4)',
                'training_samples': len(df),
                'n_features': len(feature_cols),
                'model_version': 'xgboost-1.0',
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
xgboost_forecast_service = XGBoostForecastService()
