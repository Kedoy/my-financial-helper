from django.core.management.base import BaseCommand
from apps.categories.models import Category

# Полнообразные системные категории с подходящими цветами
SYSTEM_CATEGORIES = [
    # Расходы
    {
        'name': 'Продукты',
        'type': 'expense',
        'icon': 'fa-shopping-cart',
        'color': '#10B981'  # Emerald green - свежий, ассоциируется с едой
    },
    {
        'name': 'Хозяйство',
        'type': 'expense',
        'icon': 'fa-home',
        'color': '#F59E0B'  # Amber - тёплый, домашний
    },
    {
        'name': 'Здоровье',
        'type': 'expense',
        'icon': 'fa-heart',
        'color': '#EF4444'  # Red - ассоциируется с медициной
    },
    {
        'name': 'Транспорт',
        'type': 'expense',
        'icon': 'fa-car',
        'color': '#3B82F6'  # Blue - классический для транспорта
    },
    {
        'name': 'Развлечения',
        'type': 'expense',
        'icon': 'fa-film',
        'color': '#8B5CF6'  # Purple - развлекательный, креативный
    },
    {
        'name': 'Рестораны и кафе',
        'type': 'expense',
        'icon': 'fa-utensils',
        'color': '#EC4899'  # Pink - приятный для ресторанов
    },
    {
        'name': 'Одежда и обувь',
        'type': 'expense',
        'icon': 'fa-tshirt',
        'color': '#F97316'  # Orange - модный, стильный
    },
    {
        'name': 'Электроника',
        'type': 'expense',
        'icon': 'fa-laptop',
        'color': '#6366F1'  # Indigo - технологичный
    },
    {
        'name': 'Дом и сад',
        'type': 'expense',
        'icon': 'fa-tree',
        'color': '#14B8A6'  # Teal - природный
    },
    {
        'name': 'Красота и уход',
        'type': 'expense',
        'icon': 'fa-spa',
        'color': '#EC4899'  # Pink - женственный, уход
    },
    {
        'name': 'Спорт',
        'type': 'expense',
        'icon': 'fa-dumbbell',
        'color': '#F97316'  # Orange - энергичный
    },
    {
        'name': 'Образование',
        'type': 'expense',
        'icon': 'fa-book',
        'color': '#6366F1'  # Indigo - академический
    },
    {
        'name': 'Путешествия',
        'type': 'expense',
        'icon': 'fa-plane',
        'color': '#06B6D4'  # Cyan - приключения
    },
    {
        'name': 'Подарки',
        'type': 'expense',
        'icon': 'fa-gift',
        'color': '#EC4899'  # Pink - праздничный
    },
    {
        'name': 'Животные',
        'type': 'expense',
        'icon': 'fa-paw',
        'color': '#A8A29E'  # Warm gray - натуральный
    },
    {
        'name': 'Связь и интернет',
        'type': 'expense',
        'icon': 'fa-wifi',
        'color': '#3B82F6'  # Blue - технологичный
    },
    {
        'name': 'Коммунальные услуги',
        'type': 'expense',
        'icon': 'fa-file-invoice-dollar',
        'color': '#64748B'  # Slate - серьёзный
    },
    {
        'name': 'Налоги и сборы',
        'type': 'expense',
        'icon': 'fa-landmark',
        'color': '#475569'  # Slate darker - официальный
    },
    {
        'name': 'Страхование',
        'type': 'expense',
        'icon': 'fa-shield-halved',
        'color': '#0EA5E9'  # Sky blue - защита
    },
    {
        'name': 'Инвестиции',
        'type': 'expense',
        'icon': 'fa-chart-line',
        'color': '#10B981'  # Emerald - рост
    },
    # Доходы
    {
        'name': 'Зарплата',
        'type': 'income',
        'icon': 'fa-money-bill-wave',
        'color': '#10B981'  # Emerald - деньги
    },
    {
        'name': 'Премия и бонусы',
        'type': 'income',
        'icon': 'fa-trophy',
        'color': '#F59E0B'  # Amber - достижение
    },
    {
        'name': 'Подработка',
        'type': 'income',
        'icon': 'fa-briefcase',
        'color': '#3B82F6'  # Blue - работа
    },
    {
        'name': 'Инвестиционный доход',
        'type': 'income',
        'icon': 'fa-coins',
        'color': '#10B981'  # Emerald - прибыль
    },
    {
        'name': 'Подарки и возвраты',
        'type': 'income',
        'icon': 'fa-hand-holding-dollar',
        'color': '#8B5CF6'  # Purple - приятный
    },
    {
        'name': 'Пособия и льготы',
        'type': 'income',
        'icon': 'fa-hand-holding-heart',
        'color': '#06B6D4'  # Cyan - поддержка
    },
    {
        'name': 'Стипендия',
        'type': 'income',
        'icon': 'fa-graduation-cap',
        'color': '#6366F1'  # Indigo - образование
    },
    {
        'name': 'Аренда',
        'type': 'income',
        'icon': 'fa-house-chimney',
        'color': '#14B8A6'  # Teal - недвижимость
    },
    {
        'name': 'Дивиденды',
        'type': 'income',
        'icon': 'fa-chart-pie',
        'color': '#10B981'  # Emerald - пассивный доход
    },
    {
        'name': 'Прочие доходы',
        'type': 'income',
        'icon': 'fa-plus-circle',
        'color': '#64748B'  # Slate - нейтральный
    },
]


class Command(BaseCommand):
    help = 'Настраивает системные категории для всех пользователей'

    def handle(self, *args, **kwargs):
        self.stdout.write('Начинаю настройку системных категорий...')

        # Удаляем старые системные категории
        old_system = Category.objects.filter(is_system=True)
        old_count = old_system.count()
        if old_count > 0:
            self.stdout.write(f'Удаление {old_count} старых системных категорий...')
            old_system.delete()

        # Создаём новые системные категории
        created_count = 0
        for cat_data in SYSTEM_CATEGORIES:
            category = Category.objects.create(
                name=cat_data['name'],
                type=cat_data['type'],
                icon=cat_data['icon'],
                color=cat_data['color'],
                is_system=True
            )
            created_count += 1
            self.stdout.write(f'  ✓ {category.name} ({category.type})')

        self.stdout.write(self.style.SUCCESS(
            f'\nГотово! Создано {created_count} системных категорий.'
        ))
        self.stdout.write(self.style.WARNING(
            'Системные категории защищены от удаления и редактирования.'
        ))
