from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.analytics.services.forecast_service import forecast_service
from apps.analytics.models import Forecast
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Обновить прогнозы расходов для всех пользователей с активными транзакциями'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID пользователя для обновления (опционально, по умолчанию для всех)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительное обновление даже если есть актуальный прогноз'
        )
        parser.add_argument(
            '--periods',
            type=str,
            default='7,14,30',
            help='Периоды для прогнозирования через запятую (по умолчанию: 7,14,30)'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        force = options.get('force')
        periods = [int(p.strip()) for p in options.get('periods', '7,14,30').split(',')]
        
        self.stdout.write(self.style.SUCCESS(f'Запуск обновления прогнозов...'))
        self.stdout.write(f'Периоды: {periods}')
        self.stdout.write(f'Принудительно: {force}')
        
        if user_id:
            users = User.objects.filter(id=user_id, is_active=True)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f'Пользователь с ID {user_id} не найден'))
                return
        else:
            # Получаем пользователей с транзакциями
            from apps.transactions.models import Transaction
            user_ids = Transaction.objects.values_list('user_id', flat=True).distinct()
            users = User.objects.filter(id__in=user_ids, is_active=True)
        
        total_users = users.count()
        self.stdout.write(f'Найдено {total_users} пользователей для обновления')
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for user in users:
            try:
                user_updated = False
                
                for period_days in periods:
                    # Проверяем существующий прогноз
                    existing_forecast = Forecast.objects.filter(
                        user=user,
                        forecast_type='daily',
                        period_days=period_days,
                        is_actual=True,
                        expires_at__gt=timezone.now()
                    ).first()
                    
                    # Пропускаем если есть актуальный прогноз и не force
                    if existing_forecast and not force:
                        self.stdout.write(
                            f'  Пропущено для {user.email} (период {period_days}): '
                            f'есть актуальный прогноз до {existing_forecast.expires_at}'
                        )
                        skipped_count += 1
                        continue
                    
                    # Генерируем прогноз
                    self.stdout.write(f'  Генерация прогноза для {user.email} (период {period_days})...')
                    
                    forecast_result = forecast_service.forecast_expenses(
                        user_id=user.id,
                        forecast_type='daily',
                        period_days=period_days,
                        use_cache=False  # Не используем кэш при автообновлении
                    )
                    
                    if forecast_result.get('success'):
                        # Сохраняем прогноз в БД
                        summary = forecast_result.get('summary', {})
                        model_info = forecast_result.get('model_info', {})
                        
                        forecast = Forecast.objects.create(
                            user=user,
                            forecast_type='daily',
                            period_days=period_days,
                            predicted_amount=summary.get('total_predicted', 0),
                            lower_bound=summary.get('lower_bound', 0),
                            upper_bound=summary.get('upper_bound', 0),
                            confidence=summary.get('confidence_level', 95),
                            model_version=model_info.get('model_version', ''),
                            training_data_points=model_info.get('training_data_points', 0),
                            expires_at=timezone.now() + timedelta(hours=24),
                            is_actual=True
                        )
                        
                        # Сохраняем детали прогноза
                        self._save_forecast_details(forecast, forecast_result.get('daily_forecasts', []))
                        
                        user_updated = True
                        updated_count += 1
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Прогноз сохранён: {summary.get("total_predicted", 0)} '
                                f'(диапазон: {summary.get("lower_bound", 0)} - {summary.get("upper_bound", 0)})'
                            )
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'  ✗ Ошибка прогноза для {user.email}: {forecast_result.get("error", "Неизвестно")}'
                            )
                        )
                
                # Инвалидируем старые прогнозы
                if user_updated:
                    Forecast.objects.filter(
                        user=user,
                        is_actual=True
                    ).exclude(
                        id=forecast.id if 'forecast' in locals() else None
                    ).update(is_actual=False)
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Ошибка для {user.email}: {str(e)}')
                )
        
        # Вывод статистики
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Обновлено прогнозов: {updated_count}'))
        self.stdout.write(f'Пропущено: {skipped_count}')
        self.stdout.write(self.style.ERROR(f'Ошибки: {error_count}'))
        self.stdout.write('=' * 50)
    
    def _save_forecast_details(self, forecast: Forecast, daily_forecasts: list):
        """Сохранение детализированных данных прогноза."""
        from apps.analytics.models import ForecastDetail
        
        for daily_data in daily_forecasts:
            ForecastDetail.objects.create(
                forecast=forecast,
                date=daily_data['date'],
                predicted_value=daily_data['predicted'],
                lower_bound=daily_data['lower_bound'],
                upper_bound=daily_data['upper_bound'],
                trend='unknown'
            )
