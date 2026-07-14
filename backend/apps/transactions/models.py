from django.db import models
from django.conf import settings


class Transaction(models.Model):
    """
    Финансовые транзакции.
    Упрощённая модель - без счетов.
    """
    TRANSACTION_TYPES = [
        ('expense', 'Расход'),
        ('income', 'Доход'),
    ]

    SOURCE_TYPES = [
        ('manual', 'Вручную'),
        ('sms', 'SMS'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Пользователь'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name='Категория'
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Сумма'
    )
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        default='expense',
        verbose_name='Тип'
    )
    source = models.CharField(
        max_length=10,
        choices=SOURCE_TYPES,
        default='manual',
        verbose_name='Источник'
    )
    is_ai_parsed = models.BooleanField(default=False, verbose_name='Обработано AI')
    date = models.DateTimeField(verbose_name='Дата')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['user', 'type', '-date']),
        ]

    def __str__(self):
        return f'{self.get_type_display()}: {self.amount} ({self.date})'
