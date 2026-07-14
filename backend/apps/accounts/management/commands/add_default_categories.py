from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.categories.models import Category

User = get_user_model()

DEFAULT_CATEGORIES = [
    {
        'name': 'Продукты',
        'type': 'expense',
        'icon': 'fa-shopping-cart',
        'color': '#10B981'
    },
    {
        'name': 'Хозяйство',
        'type': 'expense',
        'icon': 'fa-home',
        'color': '#F59E0B'
    },
    {
        'name': 'Здоровье',
        'type': 'expense',
        'icon': 'fa-heart',
        'color': '#EF4444'
    },
    {
        'name': 'Транспорт',
        'type': 'expense',
        'icon': 'fa-car',
        'color': '#3B82F6'
    },
    {
        'name': 'Развлечения',
        'type': 'expense',
        'icon': 'fa-film',
        'color': '#8B5CF6'
    },
    {
        'name': 'Рестораны и кафе',
        'type': 'expense',
        'icon': 'fa-utensils',
        'color': '#EC4899'
    },
    {
        'name': 'Зарплата',
        'type': 'income',
        'icon': 'fa-money-bill-wave',
        'color': '#10B981'
    },
]


class Command(BaseCommand):
    help = 'Добавляет стандартные категории всем существующим пользователям'

    def handle(self, *args, **kwargs):
        self.stdout.write('Начинаю добавление стандартных категорий...')

        users = User.objects.all()
        total_users = users.count()
        self.stdout.write(f'Найдено пользователей: {total_users}')

        created_count = 0
        skipped_count = 0

        for user in users:
            for cat_data in DEFAULT_CATEGORIES:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    type=cat_data['type'],
                    user=user,
                    defaults={
                        'icon': cat_data['icon'],
                        'color': cat_data['color'],
                        'is_system': False
                    }
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Создано категорий: {created_count}, пропущено (уже существуют): {skipped_count}'
        ))
