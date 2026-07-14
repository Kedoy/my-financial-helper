from django.db import migrations

def create_system_categories(apps, schema_editor):
    """Создаёт системные категории с правильными иконками и цветами."""
    Category = apps.get_model('categories', 'Category')
    
    # Системные категории расходов (name, icon, color)
    # Иконки Font Awesome 6.5.1
    expense_categories = [
        ('Продукты', 'cart-shopping', '#EF4444'),  # Красный
        ('Рестораны и кафе', 'utensils', '#F97316'),  # Оранжевый
        ('Транспорт', 'bus', '#F59E0B'),  # Янтарный
        ('Такси', 'taxi', '#FBBF24'),  # Жёлтый
        ('Топливо', 'gas-pump', '#FCD34D'),  # Светло-жёлтый
        ('Дом и сад', 'house', '#84CC16'),  # Лайм
        ('Коммунальные услуги', 'wrench', '#A3E635'),  # Светло-зелёный
        ('Аренда', 'house-user', '#22C55E'),  # Зелёный
        ('Интернет и связь', 'phone', '#10B981'),  # Изумрудный
        ('Здоровье', 'hospital', '#14B8A6'),  # Бирюзовый
        ('Красота и уход', 'spa', '#06B6D4'),  # Циан
        ('Одежда и обувь', 'shirt', '#0EA5E9'),  # Голубой
        ('Развлечения', 'film', '#3B82F6'),  # Синий
        ('Путешествия', 'plane', '#6366F1'),  # Индиго
        ('Образование', 'graduation-cap', '#8B5CF6'),  # Фиолетовый
        ('Книги', 'book-open', '#A78BFA'),  # Светло-фиолетовый
        ('Спорт', 'basketball', '#C084FC'),  # Пурпурный
        ('Животные', 'paw', '#E879F9'),  # Розовый
        ('Подарки', 'gift', '#F472B6'),  # Светло-розовый
        ('Налоги и сборы', 'building-columns', '#FB7185'),  # Светло-красный
        ('Страхование', 'shield-halved', '#F43F5E'),  # Розово-красный
        ('Инвестиции', 'chart-line', '#10B981'),  # Изумрудный
        ('Бытовая техника', 'house-chimney-wrench', '#64748B'),  # Серый
        ('Мебель', 'couch', '#475569'),  # Тёмно-серый
        ('Ремонт', 'screwdriver-wrench', '#334155'),  # Сланцевый
        ('Дети', 'child-reaching', '#FBBF24'),  # Янтарный
        ('Кредиты', 'credit-card', '#DC2626'),  # Тёмно-красный
        ('Другое', 'ellipsis', '#9CA3AF'),  # Светло-серый
    ]
    
    # Системные категории доходов
    income_categories = [
        ('Зарплата', 'briefcase', '#22C55E'),  # Зелёный
        ('Премия', 'trophy', '#10B981'),  # Изумрудный
        ('Подработка', 'pen-nib', '#34D399'),  # Светло-изумрудный
        ('Аренда', 'house-user', '#6EE7B7'),  # Мятный
        ('Дивиденды', 'chart-line', '#A7F3D0'),  # Светло-мятный
        ('Проценты', 'building-columns', '#059669'),  # Тёмно-зелёный
        ('Подарки', 'gift', '#D946EF'),  # Фуксия
        ('Возвраты', 'rotate-left', '#E879F9'),  # Светло-фиолетовый
        ('Налоги', 'receipt', '#A78BFA'),  # Фиолетовый
        ('Пособия', 'headset', '#8B5CF6'),  # Светло-фиолетовый
        ('Другое', 'ellipsis', '#6B7280'),  # Серый
    ]
    
    for name, icon, color in expense_categories:
        Category.objects.get_or_create(
            name=name,
            type='expense',
            is_system=True,
            defaults={
                'icon': icon,
                'color': color,
            }
        )
    
    for name, icon, color in income_categories:
        Category.objects.get_or_create(
            name=name,
            type='income',
            is_system=True,
            defaults={
                'icon': icon,
                'color': color,
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_system_categories, reverse_code=migrations.RunPython.noop),
    ]
