"""
Скрипт для проверки качества модели прогнозирования.
Проверяет точность прогноза на исторических данных.

Использование:
    python manage.py shell < validate_forecast.py
"""
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from django.db.models import Sum, Count, Avg
from apps.accounts.models import User
from apps.transactions.models import Transaction
from apps.analytics.services.forecast_service import ProphetForecastService
import json


def validate_forecast_accuracy(user_id: int, days_back: int = 30):
    """
    Проверка точности прогноза.
    
    Метод:
    1. Берём исторические данные за N дней назад
    2. Делаем прогноз на "будущее" (которое уже наступило)
    3. Сравниваем прогноз с фактическими данными
    4. Вычисляем метрики: MAE, MAPE, RMSE
    """
    print("=" * 70)
    print(f"ПРОВЕРКА КАЧЕСТВА ПРОГНОЗА (пользователь {user_id})")
    print("=" * 70)
    
    user = User.objects.get(id=user_id)
    today = timezone.now().date()
    test_start = today - timedelta(days=days_back * 2)
    test_end = today - timedelta(days=days_back)
    
    print(f"\n📅 Период проверки: {test_start} → {test_end}")
    print(f"📊 Дней для проверки: {days_back}")
    
    # Проверяем, есть ли данные
    actual_data = Transaction.objects.filter(
        user=user,
        type='expense',
        date__range=[test_start, test_end]
    ).extra(select={'date_only': 'DATE(date)'}).values('date_only').annotate(
        total=Sum('amount')
    ).order_by('date_only')
    
    if actual_data.count() < 10:
        print(f"\n❌ Недостаточно данных для проверки (найдено {actual_data.count()}, нужно ≥10)")
        return
    
    # Получаем фактические суммы
    actual_totals = {item['date_only']: float(item['total']) for item in actual_data}
    
    # Генерируем прогноз (как будто мы в test_start)
    print(f"\n🤖 Генерация прогноза...")
    service = ProphetForecastService()
    
    # Подготовка данных (только что было до test_start)
    training_data = service._prepare_training_data(user_id)
    
    if not training_data:
        print("❌ Недостаточно данных для обучения")
        return
    
    # Фильтруем training data до test_start
    training_data_filtered = [
        d for d in training_data 
        if d['ds'] < test_start.isoformat()
    ]
    
    if len(training_data_filtered) < 30:
        print(f"❌ Недостаточно данных для обучения (найдено {len(training_data_filtered)}, нужно ≥30)")
        return
    
    print(f"✓ Точек для обучения: {len(training_data_filtered)}")
    
    # Обучаем модель
    model = service._create_prophet_model(training_data_filtered)
    
    # Делаем прогноз на days_back дней
    forecast_df = service._generate_forecast(model, days_back)
    
    # Обрабатываем результаты
    import pandas as pd
    forecast_df['ds'] = pd.to_datetime(forecast_df['ds']).dt.date
    
    # Берём только даты из тестового периода
    forecast_df = forecast_df[
        (forecast_df['ds'] >= test_start) & 
        (forecast_df['ds'] <= test_end)
    ]
    
    if len(forecast_df) == 0:
        print("❌ Нет прогноза для тестового периода")
        return
    
    # Сравниваем прогноз с фактом
    print(f"\n📈 Сравнение прогноза с фактическими данными:")
    print("-" * 70)
    
    errors = []
    for _, row in forecast_df.iterrows():
        date = row['ds']
        predicted = row['yhat']
        
        # Ищем фактическое значение
        date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)
        actual = actual_totals.get(date_str, None)
        
        if actual is not None:
            error = abs(predicted - actual)
            errors.append(error)
            
            status = "✓" if error < actual * 0.2 else "⚠"  # ±20%
            print(f"  {date}: прогноз={predicted:,.0f}, факт={actual:,.0f}, ошибка={error:,.0f} ({error/actual*100:.1f}%) {status}")
    
    if not errors:
        print("❌ Не удалось сравнить ни одного значения")
        return
    
    # Вычисляем метрики
    import numpy as np
    errors = np.array(errors)
    actual_values = np.array(list(actual_totals.values())[:len(errors)])
    
    mae = errors.mean()  # Mean Absolute Error
    mape = (errors / actual_values).mean() * 100  # Mean Absolute Percentage Error
    rmse = np.sqrt((errors ** 2).mean())  # Root Mean Squared Error
    
    print("\n" + "=" * 70)
    print("📊 МЕТРИКИ КАЧЕСТВА")
    print("=" * 70)
    print(f"  MAE (Средняя абсолютная ошибка): {mae:,.2f} ₽")
    print(f"  MAPE (Средняя % ошибка): {mape:.2f}%")
    print(f"  RMSE (Среднеквадратичная ошибка): {rmse:,.2f} ₽")
    print()
    
    # Оценка качества
    if mape < 10:
        quality = "🟢 ОТЛИЧНО"
    elif mape < 20:
        quality = "🟡 ХОРОШО"
    elif mape < 30:
        quality = "🟠 УДОВЛЕТВОРИТЕЛЬНО"
    else:
        quality = "🔴 ПЛОХО"
    
    print(f"  Оценка качества: {quality}")
    print("=" * 70)
    
    return {
        'mae': mae,
        'mape': mape,
        'rmse': rmse,
        'quality': quality,
        'data_points': len(errors)
    }


def analyze_training_data(user_id: int):
    """Анализ данных для обучения."""
    print("=" * 70)
    print(f"АНАЛИЗ ДАННЫХ ДЛЯ ОБУЧЕНИЯ (пользователь {user_id})")
    print("=" * 70)
    
    user = User.objects.get(id=user_id)
    
    # Все транзакции
    all_transactions = Transaction.objects.filter(
        user=user,
        type='expense'
    ).order_by('date')
    
    if all_transactions.count() == 0:
        print("❌ Нет транзакций")
        return
    
    # Статистика
    first_date = all_transactions.first().date
    last_date = all_transactions.last().date
    total_days = (last_date - first_date).days + 1
    
    # Уникальные даты
    unique_dates = all_transactions.extra(
        select={'date_only': 'DATE(date)'}
    ).values('date_only').distinct().count()
    
    # Суммы
    total_amount = all_transactions.aggregate(Sum('amount'))['amount__sum']
    avg_daily = all_transactions.extra(
        select={'date_only': 'DATE(date)'}
    ).values('date_only').annotate(
        daily_sum=Sum('amount')
    ).aggregate(Avg('daily_sum'))['daily_sum__avg'] or 0
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"  Всего транзакций: {all_transactions.count()}")
    print(f"  Период: {first_date.date()} → {last_date.date()} ({total_days} дней)")
    print(f"  Уникальных дней с тратами: {unique_dates}")
    print(f"  Общая сумма: {total_amount:,.2f} ₽")
    print(f"  Средний день: {avg_daily:,.2f} ₽")
    print()
    
    # Проверка достаточности данных
    print("📋 ТРЕБОВАНИЯ ДЛЯ ОБУЧЕНИЯ:")
    print(f"  Минимум 30 уникальных дней: {'✓' if unique_dates >= 30 else '✗'} ({unique_dates})")
    print(f"  Минимум 60 дней истории: {'✓' if total_days >= 60 else '⚠'} ({total_days})")
    print()
    
    if unique_dates < 30:
        print(f"⚠️  Недостаточно данных! Нужно ещё {30 - unique_dates} дней с транзакциями.")
    else:
        print("✓ Данных достаточно для обучения модели")
    
    # Распределение по месяцам (упрощённо)
    print("\n📅 ПОСЛЕДНИЕ ТРАНЗАКЦИИ:")
    recent = all_transactions.order_by('-date')[:5]
    for t in recent:
        print(f"  {t.date.date()}: {t.amount:,.2f} ₽")


if __name__ == '__main__':
    # Пример использования
    print("\n💡 Использование:")
    print("  from apps.analytics.tests.validate_model import analyze_training_data, validate_forecast_accuracy")
    print("  analyze_training_data(user_id=5)")
    print("  validate_forecast_accuracy(user_id=5, days_back=14)")
    print()
    print("  # Сравнительный анализ моделей:")
    print("  from apps.analytics.services.model_comparison import run_comparison")
    print("  run_comparison(user_id=5, test_days=14)")
    print()
    
    # Для тестового пользователя
    try:
        user = User.objects.filter(email='forecast_test@example.com').first()
        if user:
            analyze_training_data(user.id)
            print("\n")
            validate_forecast_accuracy(user.id, days_back=14)
            
            # Сравнительный анализ
            print("\n")
            print("=" * 70)
            print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ МОДЕЛЕЙ")
            print("=" * 70)
            from apps.analytics.services.model_comparison import run_comparison
            run_comparison(user.id, test_days=14)
    except Exception as e:
        print(f"Ошибка: {e}")
