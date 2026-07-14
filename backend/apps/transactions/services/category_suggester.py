"""
Сервис для автоматической категоризации транзакций.
Использует ключевые слова для определения категории.
"""

from typing import Optional
from apps.categories.models import Category


# Словарь ключевых слов для категорий
CATEGORY_KEYWORDS = {
    'Продукты': {
        'keywords': ['магнит', 'пятёрочка', 'перекрёсток', 'лента', 'auchan', 'продукты', 'еда', 
                     'pyaterochka', 'magnit', 'dixy', 'дикси', 'окей', 'okei', 'metro', 'метро кэш'],
        'type': 'expense'
    },
    'Транспорт': {
        'keywords': ['такси', 'uber', 'yandex', 'яндекс', 'метро', 'автобус', 'бензин', 'лукойл', 
                     'газпром', 'роснефть', 'bp', 'shell', 'taxi', 'metro transport'],
        'type': 'expense'
    },
    'Кафе и рестораны': {
        'keywords': ['ресторан', 'кафе', 'бар', 'starbucks', 'kofe', 'макдоналдс', 'mcdonalds', 
                     'kfc', 'burger king', 'пиццерия', 'pizza', 'суши', 'wok'],
        'type': 'expense'
    },
    'Развлечения': {
        'keywords': ['кино', 'театр', 'концерт', 'парк', 'зоопарк', 'караоке', 'боулинг', 
                     'cinema', 'movie', 'entertainment'],
        'type': 'expense'
    },
    'Здоровье': {
        'keywords': ['аптека', 'больница', 'клиника', 'врач', 'лекарства', 'medicine', 
                     'pharmacy', 'apteka', 'здравсити', 'еаптека'],
        'type': 'expense'
    },
    'Покупки': {
        'keywords': ['магазин', 'ozon', 'wildberries', 'lamoda', 'одежда', 'обувь', 'shopping', 
                     'mall', 'torg', 'торговый центр'],
        'type': 'expense'
    },
    'Связь и интернет': {
        'keywords': ['связь', 'интернет', 'мобильный', 'хостинг', 'подписка', 'beeline', 
                     'mts', 'megafon', 'tele2', 'yota', 'subscription'],
        'type': 'expense'
    },
    'Жильё и коммунальные услуги': {
        'keywords': ['аренда', 'коммуналка', 'электричество', 'вода', 'газ', 'rent', 'utility', 
                     'housing', 'жкх', 'управляющая компания'],
        'type': 'expense'
    },
    'Зарплата': {
        'keywords': ['зарплата', 'salary', 'wage', 'payroll', 'аванс', 'премия', 'bonus'],
        'type': 'income'
    },
    'Переводы': {
        'keywords': ['перевод', 'transfer', 'p2p', 'счёт', 'invoice'],
        'type': 'income'
    },
}


def suggest_category(description: str, transaction_type: str = 'expense') -> Optional[Category]:
    """
    Предложить категорию на основе описания транзакции.
    
    Args:
        description: Описание транзакции
        transaction_type: Тип транзакции (expense/income)
    
    Returns:
        Category или None
    """
    if not description:
        return None
    
    description_lower = description.lower()
    
    for category_name, data in CATEGORY_KEYWORDS.items():
        # Пропускаем категории с неподходящим типом
        if data['type'] != transaction_type:
            continue
        
        for keyword in data['keywords']:
            if keyword.lower() in description_lower:
                # Ищем системную категорию или создаём
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    type=transaction_type,
                    defaults={
                        'is_system': True,
                        'icon': get_default_icon(category_name),
                        'color': get_default_color(category_name)
                    }
                )
                return category
    
    return None


def get_default_icon(category_name: str) -> str:
    """Возвращает иконку по умолчанию для категории."""
    icons = {
        'Продукты': 'shopping_cart',
        'Транспорт': 'directions_car',
        'Кафе и рестораны': 'restaurant',
        'Развлечения': 'theater_comedy',
        'Здоровье': 'local_hospital',
        'Покупки': 'shopping_bag',
        'Связь и интернет': 'phone_android',
        'Жильё и коммунальные услуги': 'home',
        'Зарплата': 'attach_money',
        'Переводы': 'swap_horiz',
    }
    return icons.get(category_name, 'category')


def get_default_color(category_name: str) -> str:
    """Возвращает цвет по умолчанию для категории."""
    colors = {
        'Продукты': '#4CAF50',
        'Транспорт': '#2196F3',
        'Кафе и рестораны': '#FF9800',
        'Развлечения': '#9C27B0',
        'Здоровье': '#F44336',
        'Покупки': '#E91E63',
        'Связь и интернет': '#00BCD4',
        'Жильё и коммунальные услуги': '#795548',
        'Зарплата': '#8BC34A',
        'Переводы': '#607D8B',
    }
    return colors.get(category_name, '#9E9E9E')


def categorize_transactions(transactions_queryset):
    """
    Массовая категоризация транзакций.
    
    Args:
        transactions_queryset: QuerySet транзакций без категории
    
    Returns:
        Количество категоризированных транзакций
    """
    count = 0
    for transaction in transactions_queryset:
        if not transaction.category and transaction.description:
            category = suggest_category(transaction.description, transaction.type)
            if category:
                transaction.category = category
                transaction.is_ai_parsed = True
                transaction.save(update_fields=['category', 'is_ai_parsed'])
                count += 1
    return count
