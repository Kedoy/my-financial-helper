from django.db import models
from django.conf import settings


class Forecast(models.Model):
    """
    Прогнозы расходов на основе Prophet.
    Кэширует результаты предсказаний для каждого пользователя.
    """
    FORECAST_TYPES = [
        ('daily', 'Дневной'),
        ('weekly', 'Недельный'),
        ('monthly', 'Месячный'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forecasts',
        verbose_name='Пользователь'
    )
    forecast_type = models.CharField(
        max_length=10,
        choices=FORECAST_TYPES,
        default='daily',
        verbose_name='Тип прогноза'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='forecasts',
        verbose_name='Категория (опционально)'
    )
    period_days = models.PositiveIntegerField(
        default=30,
        verbose_name='Период прогноза (дней)'
    )
    predicted_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Прогнозируемая сумма'
    )
    lower_bound = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Нижняя граница (доверительный интервал)'
    )
    upper_bound = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Верхняя граница (доверительный интервал)'
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=95.00,
        verbose_name='Уровень доверия (%)'
    )
    model_version = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Версия модели'
    )
    training_data_points = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество точек обучения'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name='Действителен до')
    is_actual = models.BooleanField(default=True, verbose_name='Актуален')

    class Meta:
        db_table = 'forecasts'
        verbose_name = 'Прогноз'
        verbose_name_plural = 'Прогнозы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'forecast_type', '-created_at']),
            models.Index(fields=['user', 'is_actual']),
            models.Index(fields=['user', 'category', 'is_actual']),
        ]

    def __str__(self):
        category_str = f' ({self.category.name})' if self.category else ''
        return f'Прогноз для {self.user}{category_str}: {self.predicted_amount}'


class ForecastDetail(models.Model):
    """
    Детализированные данные прогноза по дням.
    """
    forecast = models.ForeignKey(
        Forecast,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='Прогноз'
    )
    date = models.DateField(verbose_name='Дата')
    predicted_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Прогнозируемое значение'
    )
    lower_bound = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Нижняя граница'
    )
    upper_bound = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Верхняя граница'
    )
    trend = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Тренд'
    )

    class Meta:
        db_table = 'forecast_details'
        verbose_name = 'Деталь прогноза'
        verbose_name_plural = 'Детали прогноза'
        ordering = ['date']
        unique_together = ['forecast', 'date']
        indexes = [
            models.Index(fields=['forecast', 'date']),
        ]

    def __str__(self):
        return f'{self.date}: {self.predicted_value}'
