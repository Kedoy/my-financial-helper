"""
Сервис для парсинга SMS от банков.
Поддерживает основные банки России: Сбербанк, Тинькофф, Альфа-Банк.
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any


# Паттерны для основных банков России
BANK_PATTERNS = {
    'sberbank': {
        'phone': ['900', '+79000000900', '79000000900'],
        'patterns': [
            # "Pokupka 1500.00 RUB. Karta *1234. Magazit 'Produkti'. Ost. 25000.00 RUB"
            r'(?:Pokupka|Списание)\s+([\d\s]+\.?\d*)\s*(?:RUB|₽|rub|руб).*?(?:карт[аы]\s?\*?(\d{4}))?.*?(?:Магазин|в|M)\s*[\'"]?([^\'".]+)',
            # "1500.00 RUB списано с карты *5678 в магазине PYATEROCHKA"
            r'([\d\s]+\.?\d*)\s*(?:RUB|₽|руб)\s+(?:списано|зачислено).*?карт[аы]\s?\*?(\d{4}).*?(?:в\s+)?([^.\n]+)',
            # "Card *9876: 3500 RUB. Berezka. Balance: 15000 RUB"
            r'Card\s+\*(\d{4}).*?([\d\s]+\.?\d*)\s*(?:RUB|₽|руб).*?([A-Za-zА-Яа-я0-9\s]+)\. Balance',
        ]
    },
    'tinkoff': {
        'phone': ['+79991234567', '79991234567', '9991234567'],
        'patterns': [
            r'([\d\s]+\.?\d*)\s*(?:RUB|₽|руб)\s+списано с карты \*(\d{4}).*?в\s+([^.\n]+)',
            r'([\d\s]+\.?\d*)\s*(?:RUB|₽|руб)\s+зачислено.*?(?:с\s+)?([^.\n]+)',
            r'Card \*(\d{4}):.*?([\d\s]+\.?\d*)\s*(?:RUB|₽|руб).*?([^.\n]+)',
        ]
    },
    'alfa': {
        'phone': ['+79991234567', '79991234567', 'ALFA', 'ALPHA'],
        'patterns': [
            r'([\d\s]+\.?\d*)\s*(?:RUB|₽|руб).*(?:Списано|Зачислено).*?(?:в\s+)?([^.\n]+)',
            r'Card \*(\d{4}).*?([\d\s]+\.?\d*)\s*(?:RUB|₽|руб).*?([^.\n]+)',
        ]
    },
    'default': {
        'phone': [],
        'patterns': [
            # Универсальный паттерн для суммы
            r'([\d\s]+\.?\d*)\s*(?:RUB|₽|rub|руб)',
            # Универсальный паттерн для описания
            r'(?:в\s+|Card\s+\*\d{4}.*?)([A-Za-zА-Яа-я0-9\s\'"]{3,})',
        ]
    }
}


def parse_sms(sms_text: str, bank_phone: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Парсинг SMS от банка.
    
    Args:
        sms_text: Текст SMS сообщения
        bank_phone: Номер телефона банка (опционально)
    
    Returns:
        Dict с полями: amount, type, description, date, bank
        или None если не удалось распарсить
    """
    sms_text = sms_text.strip()
    
    # Определяем банк по номеру телефона
    bank_name = None
    if bank_phone:
        bank_phone_clean = bank_phone.replace('+', '').replace(' ', '').replace('-', '')
        for name, data in BANK_PATTERNS.items():
            if name == 'default':
                continue
            for phone in data['phone']:
                phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
                if bank_phone_clean == phone_clean or bank_phone_clean.endswith(phone_clean[-10:]):
                    bank_name = name
                    break
            if bank_name:
                break
    
    # Если банк не найден по номеру, пробуем найти по ключевым словам в тексте
    if not bank_name:
        sms_lower = sms_text.lower()
        if 'sber' in sms_lower or 'сбер' in sms_lower or '900' in sms_text:
            bank_name = 'sberbank'
        elif 'tinkoff' in sms_lower or 'тинькофф' in sms_lower:
            bank_name = 'tinkoff'
        elif 'alfa' in sms_lower or 'альфа' in sms_lower:
            bank_name = 'alfa'
    
    # Определяем, какие паттерны использовать
    banks_to_try = [bank_name] if bank_name else list(BANK_PATTERNS.keys())
    if 'default' not in banks_to_try:
        banks_to_try.append('default')
    
    for bank in banks_to_try:
        if bank not in BANK_PATTERNS:
            continue
            
        patterns = BANK_PATTERNS[bank]['patterns']
        
        for pattern in patterns:
            try:
                match = re.search(pattern, sms_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    groups = match.groups()
                    
                    # Пытаемся найти сумму в группах
                    amount = None
                    description = None
                    
                    for group in groups:
                        if group is None:
                            continue
                        # Проверяем, похоже ли на сумму
                        cleaned = group.replace(' ', '').replace(',', '.')
                        try:
                            potential_amount = float(cleaned)
                            if amount is None and potential_amount > 0:
                                amount = potential_amount
                        except ValueError:
                            # Если не число, то это описание
                            if description is None and len(group.strip()) > 2:
                                description = group.strip()
                    
                    if amount is None:
                        continue
                    
                    # Определяем тип транзакции
                    type_ = 'expense'
                    sms_lower = sms_text.lower()
                    if any(word in sms_lower for word in ['зачислено', 'поступление', 'пополнение', 'перевод вам', 'credited', 'deposit']):
                        type_ = 'income'
                    
                    # Если описание не найдено, берём часть текста
                    if not description:
                        # Извлекаем текст после суммы
                        desc_match = re.search(r'[\d\.]+\s*(?:RUB|₽|руб)[^.\n]*[.:\n]\s*([^.\n]+)', sms_text, re.IGNORECASE)
                        if desc_match:
                            description = desc_match.group(1).strip()
                        else:
                            description = sms_text[:50]
                    
                    return {
                        'amount': amount,
                        'type': type_,
                        'description': description,
                        'date': datetime.now(),
                        'bank': bank
                    }
            except re.error:
                continue
    
    return None


def parse_sms_batch(sms_messages: list) -> list:
    """
    Массовый парсинг SMS сообщений.
    
    Args:
        sms_messages: Список словарей с SMS [{'text': str, 'phone': str}, ...]
    
    Returns:
        Список распарсенных транзакций
    """
    results = []
    for sms in sms_messages:
        parsed = parse_sms(sms.get('text', ''), sms.get('phone'))
        if parsed:
            results.append(parsed)
    return results
