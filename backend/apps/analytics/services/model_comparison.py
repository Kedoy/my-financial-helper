"""
Сервис сравнительного анализа моделей прогнозирования.

Для научной конференции:
- Сравнивает Prophet, LSTM, XGBoost
- Вычисляет метрики качества (MAE, MAPE, RMSE)
- Строит сравнительные отчёты
"""
import numpy as np
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from apps.transactions.models import Transaction
from apps.analytics.services.forecast_service import forecast_service as prophet_service
from typing import Dict, List, Any, Optional


class ModelComparisonService:
    """
    Сравнительный анализ моделей прогнозирования.
    
    Метрики:
    - MAE (Mean Absolute Error)
    - MAPE (Mean Absolute Percentage Error)
    - RMSE (Root Mean Squared Error)
    - R² (Coefficient of Determination)
    """
    
    def __init__(self):
        self.models = {
            'Prophet': prophet_service,
            # 'LSTM': lstm_forecast_service,  # Можно добавить позже
            # 'XGBoost': xgboost_forecast_service,
        }
    
    def compare_models(
        self,
        user_id: int,
        test_days: int = 14,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
        Сравнение всех моделей на исторических данных.
        
        Args:
            user_id: ID пользователя
            test_days: Количество дней для тестирования
            forecast_days: Горизонт прогнозирования
            
        Returns:
            Отчёт со сравнением моделей
        """
        print("=" * 70)
        print(f"СРАВНИТЕЛЬНЫЙ АНАЛИЗ МОДЕЛЕЙ (пользователь {user_id})")
        print("=" * 70)
        
        # Подготовка тестовых данных
        test_data = self._prepare_test_data(user_id, test_days)
        
        if test_data is None:
            return {
                'success': False,
                'error': 'Недостаточно данных для сравнительного анализа'
            }
        
        results = {}
        
        # Тестирование каждой модели
        for model_name, model_service in self.models.items():
            print(f"\n🔬 Тестирование модели: {model_name}")
            print("-" * 50)
            
            try:
                # Получаем прогноз
                forecast_result = model_service.forecast_expenses(
                    user_id=user_id,
                    forecast_days=forecast_days,
                    use_cache=False
                )
                
                if not forecast_result.get('success'):
                    print(f"  ✗ Ошибка: {forecast_result.get('error', 'Неизвестно')}")
                    results[model_name] = {
                        'success': False,
                        'error': forecast_result.get('error')
                    }
                    continue
                
                # Вычисляем метрики
                metrics = self._calculate_metrics(
                    forecast=forecast_result,
                    actual_data=test_data
                )
                
                results[model_name] = {
                    'success': True,
                    'forecast': forecast_result,
                    'metrics': metrics
                }
                
                print(f"  ✓ MAE:  {metrics['mae']:.2f} ₽")
                print(f"  ✓ MAPE: {metrics['mape']:.2f}%")
                print(f"  ✓ RMSE: {metrics['rmse']:.2f} ₽")
                
            except Exception as e:
                print(f"  ✗ Исключение: {str(e)}")
                results[model_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Формирование отчёта
        report = self._generate_report(results, test_data)
        
        print("\n" + "=" * 70)
        print("ИТОГОВЫЙ ОТЧЁТ")
        print("=" * 70)
        print(self._format_report(report))
        
        return report
    
    def _prepare_test_data(
        self,
        user_id: int,
        test_days: int
    ) -> Optional[Dict[str, float]]:
        """
        Подготовка фактических данных для тестирования.
        """
        today = timezone.now().date()
        test_start = today - timedelta(days=test_days)
        
        transactions = Transaction.objects.filter(
            user_id=user_id,
            type='expense',
            date__range=[test_start, today]
        ).extra(
            select={'date_only': 'DATE(date)'}
        ).values('date_only').annotate(
            total=Sum('amount')
        ).order_by('date_only')
        
        if transactions.count() < test_days * 0.5:
            return None
        
        # Преобразуем в словарь {date: amount}
        data = {}
        for item in transactions:
            date_str = item['date_only']
            data[date_str] = float(item['total'])
        
        return data
    
    def _calculate_metrics(
        self,
        forecast: Dict[str, Any],
        actual_data: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Вычисление метрик качества прогноза.
        """
        daily_forecasts = forecast.get('daily_forecasts', [])
        
        if not daily_forecasts:
            return {
                'mae': 0,
                'mape': 0,
                'rmse': 0,
                'r2': 0
            }
        
        # Сопоставление прогноза с фактом
        errors = []
        percentage_errors = []
        predictions = []
        actuals = []
        
        for daily in daily_forecasts:
            date = daily['date']
            predicted = daily['predicted']
            
            if date in actual_data:
                actual = actual_data[date]
                error = abs(predicted - actual)
                errors.append(error)
                
                if actual != 0:
                    percentage_error = (error / actual) * 100
                    percentage_errors.append(percentage_error)
                
                predictions.append(predicted)
                actuals.append(actual)
        
        if not errors:
            return {
                'mae': 0,
                'mape': 0,
                'rmse': 0,
                'r2': 0,
                'data_points': 0
            }
        
        # MAE (Mean Absolute Error)
        mae = np.mean(errors)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(percentage_errors) if percentage_errors else 0
        
        # RMSE (Root Mean Squared Error)
        rmse = np.sqrt(np.mean(np.array(errors) ** 2))
        
        # R² (Coefficient of Determination)
        if len(actuals) > 1:
            ss_res = np.sum((np.array(actuals) - np.array(predictions)) ** 2)
            ss_tot = np.sum((np.array(actuals) - np.mean(actuals)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        else:
            r2 = 0
        
        return {
            'mae': float(mae),
            'mape': float(mape),
            'rmse': float(rmse),
            'r2': float(r2),
            'data_points': len(errors)
        }
    
    def _generate_report(
        self,
        results: Dict[str, Any],
        test_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Генерация итогового отчёта.
        """
        # Сводка по моделям
        models_summary = []
        
        for model_name, result in results.items():
            if not result.get('success'):
                models_summary.append({
                    'name': model_name,
                    'success': False,
                    'error': result.get('error')
                })
                continue
            
            metrics = result.get('metrics', {})
            forecast = result.get('forecast', {})
            
            models_summary.append({
                'name': model_name,
                'success': True,
                'mae': metrics.get('mae', 0),
                'mape': metrics.get('mape', 0),
                'rmse': metrics.get('rmse', 0),
                'r2': metrics.get('r2', 0),
                'total_predicted': forecast.get('summary', {}).get('total_predicted', 0),
                'trend': forecast.get('trend', {}).get('direction', 'unknown'),
                'data_points': metrics.get('data_points', 0)
            })
        
        # Определение лучшей модели
        successful_models = [m for m in models_summary if m.get('success')]
        
        best_model = None
        if successful_models:
            # Лучшая по MAPE (меньше = лучше)
            best_model = min(successful_models, key=lambda x: x['mape'])
        
        # Статистика данных
        actual_values = list(test_data.values())
        
        report = {
            'success': True,
            'test_period_days': len(test_data),
            'actual_total': sum(actual_values),
            'actual_average': np.mean(actual_values) if actual_values else 0,
            'models': models_summary,
            'best_model': best_model,
            'generated_at': timezone.now().isoformat()
        }
        
        return report
    
    def _format_report(self, report: Dict[str, Any]) -> str:
        """
        Форматирование отчёта для вывода.
        """
        lines = []
        
        lines.append(f"Период теста: {report['test_period_days']} дней")
        lines.append(f"Фактическая сумма: {report['actual_total']:,.2f} ₽")
        lines.append(f"Фактическое среднее: {report['actual_average']:,.2f} ₽/день")
        lines.append("")
        
        # Таблица результатов
        lines.append("┌─────────────┬──────────┬──────────┬──────────┬────────┐")
        lines.append("│ Модель      │   MAE    │   MAPE   │   RMSE   │  R²    │")
        lines.append("├─────────────┼──────────┼──────────┼──────────┼────────┤")
        
        for model in report['models']:
            if not model.get('success'):
                lines.append(f"│ {model['name']:<11} │ {'Ошибка':<8} │    -     │    -     │   -    │")
            else:
                lines.append(
                    f"│ {model['name']:<11} │ {model['mae']:>6.2f}   │ {model['mape']:>6.2f}%  │ {model['rmse']:>6.2f}   │ {model['r2']:>5.3f} │"
                )
        
        lines.append("└─────────────┴──────────┴──────────┴──────────┴────────┘")
        
        if report.get('best_model'):
            best = report['best_model']
            lines.append("")
            lines.append(f"🏆 Лучшая модель: {best['name']} (MAPE: {best['mape']:.2f}%)")
        
        return "\n".join(lines)


# Singleton
model_comparison_service = ModelComparisonService()


def run_comparison(user_id: int, test_days: int = 14):
    """
    Быстрый запуск сравнительного анализа.
    
    Использование:
        from apps.analytics.services.model_comparison import run_comparison
        run_comparison(user_id=5)
    """
    return model_comparison_service.compare_models(
        user_id=user_id,
        test_days=test_days
    )
