from django.db import models
from django.conf import settings


class Category(models.Model):
    """
    Категории для транзакций.
    Могут быть системными (общими для всех) или пользовательскими.
    """
    TRANSACTION_TYPES = [
        ('expense', 'Расход'),
        ('income', 'Доход'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название')
    type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        default='expense',
        verbose_name='Тип'
    )
    icon = models.CharField(max_length=50, default='default', help_text='Название иконки')
    color = models.CharField(max_length=7, default='#3498db', help_text='Цвет в формате HEX')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categories',
        verbose_name='Пользователь'
    )
    is_system = models.BooleanField(default=False, help_text='Системная категория')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['type', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name', 'type'],
                name='unique_user_category'
            ),
            models.UniqueConstraint(
                fields=['name', 'type'],
                condition=models.Q(is_system=True),
                name='unique_system_category'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'
