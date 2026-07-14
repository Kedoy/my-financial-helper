"""
OpenRouter AI Service for financial insights.
Uses OpenRouter API to access various LLM models.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Загружаем .env явно
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / '.env')


class OpenRouterService:
    """Сервис для работы с OpenRouter AI API."""

    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.model = os.getenv('AI_MODEL', 'arcee-ai/trinity-mini:free')
        self.site_url = os.getenv('SITE_URL', 'http://localhost:5173')
        self.site_name = os.getenv('SITE_NAME', 'Ks Financial App')
    
    def analyze_financial_data(self, financial_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Анализирует финансовые данные и возвращает рекомендации.

        Args:
            financial_data: Словарь с финансовыми данными

        Returns:
            Список рекомендаций в формате [{"category": "...", "insight": "...", "type": "..."}]
        """
        if not self.api_key:
            print('[OpenRouter] API key not set, using fallback insights')
            return self._get_fallback_insights(financial_data)

        prompt = self._build_prompt(financial_data)

        try:
            print(f'[OpenRouter] Sending request with model: {self.model}')
            response = self._make_request(prompt)
            print(f'[OpenRouter] Received response: {response[:100]}...')
            insights = self._parse_response(response, financial_data)
            print(f'[OpenRouter] Parsed {len(insights)} insights')
            
            # Постобработка: нормализация типов и количества
            insights = self._normalize_insights(insights, financial_data)
            print(f'[OpenRouter] Normalized to {len(insights)} insights')
            
            return insights[:5]  # Максимум 5 рекомендаций

        except requests.exceptions.HTTPError as e:
            error_msg = f'HTTP Error {e.response.status_code}: {e.response.text[:200] if e.response.text else "No details"}'
            print(f'[OpenRouter] {error_msg}')

            # Обработка rate limit (429)
            if e.response.status_code == 429:
                retry_after = e.response.headers.get('Retry-After', '60')
                print(f'[OpenRouter] Rate limit exceeded. Retry after {retry_after} seconds')
                return self._get_fallback_insights(financial_data, 'Превышен лимит запросов. Попробуйте через минуту.')

            if e.response.status_code == 401:
                return self._get_fallback_insights(financial_data, 'Неверный OPENROUTER_API_KEY')
            elif e.response.status_code == 404:
                return self._get_fallback_insights(financial_data, f'Модель не найдена: {self.model}')
            return self._get_fallback_insights(financial_data)
        except Exception as e:
            print(f'[OpenRouter] API error: {type(e).__name__}: {e}')
            return self._get_fallback_insights(financial_data)
    
    def _build_prompt(self, data: Dict[str, Any]) -> str:
        """Строит промпт для анализа финансовых данных."""
        categories_str = ', '.join([
            f"{c['name']} ({c['total']} ₽)"
            for c in data.get('top_categories', [])
        ]) or 'Нет данных'

        # Рассчитываем дополнительные метрики для анализа
        total_expenses = data.get('total_expenses', 0)
        total_income = data.get('total_income', 0)
        expense_count = data.get('expense_count', 0)
        income_count = data.get('income_count', 0)
        
        # Средняя транзакция расхода
        avg_expense = total_expenses / expense_count if expense_count > 0 else 0
        
        # Доля топ категории
        top_category_share = 0
        if total_expenses > 0 and data.get('top_categories'):
            top_category_share = (data['top_categories'][0]['total'] / total_expenses) * 100

        return f"""Ты — помощник-аналитик личных финансов. Твоя задача — давать ТОЛЬКО ПРАКТИЧЕСКИЕ, ДЕЙСТВЕННЫЕ советы по экономии денег и улучшению финансового положения.

КРИТИЧЕСКИ ВАЖНО:
- Запрещены бессмысленные советы вроде "разбейте расходы на меньшие суммы" — это не экономит деньги
- Запрещены общие фразы "следите за расходами", "планируйте бюджет" без конкретики
- Каждая рекомендация должна отвечать на вопрос "КАК именно это сделать?" и "СКОЛЬКО я сэкономлю?"
- Используй только реальные данные пользователя (цифры, категории)

ФИНАНСОВЫЕ ДАННЫЕ:
- Период анализа: {data.get('period_days', 30)} дней
- Общие доходы: {total_income} ₽
- Общие расходы: {total_expenses} ₽
- Баланс (доходы - расходы): {data.get('balance', 0)} ₽
- Количество транзакций доходов: {income_count}
- Количество транзакций расходов: {expense_count}
- Средняя транзакция расхода: {avg_expense:.0f} ₽
- Топ категорий расходов: {categories_str}
- Доля крупнейшей категории: {top_category_share:.0f}%

ТРЕБОВАНИЯ К СТРУКТУРЕ ОТВЕТА (ОБЯЗАТЕЛЬНО):
1. Верни ответ ТОЛЬКО в формате JSON массива из 3-5 рекомендаций
2. Каждый элемент должен иметь структуру:
   {{"category": "Название", "insight": "Текст", "type": "warning|success|info"}}
3. СТРОГАЯ СТРУКТУРА ПО ТИПАМ:
   
   **success (максимум 1 рекомендация)** — Хвалебная/мотивирующая:
   - ДОПУСКАЕТСЯ ТОЛЬКО если есть реальные достижения: положительный баланс, сбережения >20% дохода, разнообразие категорий, регулярные доходы
   - ЗАПРЕЩЕНО хвалить если: расходы > доходов, есть "глупые" траты (рестораны/развлечения >30% расходов), меньше 3 транзакций
   - Если нет достижений — НЕ добавляй рекомендацию типа success вообще
   
   **warning (1-2 рекомендации)** — Негативные/критичные:
   - Указывай на ЯВНЫЕ проблемы: отрицательный баланс, одна категория >50% расходов, мало транзакций для анализа, нет доходов
   - Будь прямым и конкретным, используй цифры
   - Пример: "Расходы превышают доходы в 2 раза. Критическая ситуация."
   
   **info (1-2 рекомендации)** — Практические советы по экономии:
   - Конкретные действия: что сделать, сколько денег сэкономит
   - Избегай общих фраз — давай измеримые рекомендации
   - Пример: "На рестораны потрачено 15000 ₽ (45% расходов). Сократите до 2 раз в неделю — сэкономите ~8000 ₽/мес"

4. КОНКРЕТНЫЕ ТРЕБОВАНИЯ:
   - Используй цифры из данных (₽, проценты, количество)
   - Избегай бесполезных советов:
     ❌ "Разбейте расходы на меньшие суммы" — не экономит деньги
     ❌ "Следите за тратами" — без конкретики
     ❌ "Планируйте бюджет" — без конкретных шагов
   - Если проблема серьёзная (баланс < 0) — ставь на первое место
   - Категории должны соответствовать реальным категориям пользователя
   - НЕ добавляй текст до или после JSON
   - НЕ используй markdown разметку (```json)

5. ПРИМЕРЫ ПРАВИЛЬНЫХ ОТВЕТОВ:

Для проблемного бюджета:
[
  {{"category": "Бюджет", "insight": "Расходы превышают доходы в 2 раза. Критическая ситуация — срочно сократите траты или найдите дополнительный доход.", "type": "warning"}},
  {{"category": "Рестораны", "insight": "На рестораны потрачено 15000 ₽ (45% расходов). Это основная статья — сократите до 10% для экономии 10000 ₽/мес.", "type": "warning"}},
  {{"category": "Доходы", "insight": "Всего 1 транзакция дохода за период. Рассмотрите подработку или фриланс для стабильности.", "type": "info"}}
]

Для здорового бюджета:
[
  {{"category": "Сбережения", "insight": "Вы откладываете 25% дохода — отличный финансовый буфер! Продолжайте в том же духе.", "type": "success"}},
  {{"category": "Транспорт", "insight": "Транспорт составляет 30% расходов. Изучите возможность каршеринга или общественного транспорта.", "type": "info"}},
  {{"category": "Планирование", "insight": "Рекомендуем создать резервный фонд на 3 месяца расходов (~45000 ₽).", "type": "info"}}
]

СГЕНЕРИРУЙ АНАЛИЗ ДЛЯ ПРЕДОСТАВЛЕННЫХ ДАННЫХ:"""
    
    def _make_request(self, prompt: str) -> str:
        """Делает запрос к OpenRouter API."""
        url = f'{self.base_url}/chat/completions'

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': self.site_url,
            'X-Title': self.site_name,
        }

        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Ты — помощник-аналитик. Твоя задача — проводить глубокий анализ предоставленных данных и давать краткие, четкие выводы.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 1500,  # Увеличено для более полных ответов
        }

        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()
        print(f'[OpenRouter] Full response: {result}')
        
        # Проверяем наличие контента
        if not result.get('choices') or len(result['choices']) == 0:
            print('[OpenRouter] No choices in response')
            raise ValueError('No choices in API response')
        
        content = result['choices'][0]['message']['content']
        if not content:
            print('[OpenRouter] Empty content in response, possible model issue')
            # Пробуем альтернативную модель
            return self._retry_with_alternative_model(prompt)
        
        return content
    
    def _retry_with_alternative_model(self, prompt: str) -> str:
        """Повторяет запрос с альтернативной моделью если основная не справилась."""
        alternative_models = [
            'qwen/qwen-2.5-coder-32b-instruct:free',
            'mistralai/mistral-7b-instruct:free',
        ]
        
        for model in alternative_models:
            try:
                print(f'[OpenRouter] Retrying with alternative model: {model}')
                url = f'{self.base_url}/chat/completions'
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': self.site_url,
                    'X-Title': self.site_name,
                }
                payload = {
                    'model': model,
                    'messages': [
                        {'role': 'system', 'content': 'Ты — помощник-аналитик личных финансов.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 1500,
                }
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content')
                if content:
                    print(f'[OpenRouter] Alternative model {model} succeeded')
                    return content
            except Exception as e:
                print(f'[OpenRouter] Alternative model {model} failed: {e}')
                continue
        
        raise ValueError('All alternative models failed')
    
    def _parse_response(self, content: str, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Парсит ответ от API и возвращает список рекомендаций."""
        import json

        print(f'[OpenRouter] Raw content: {content[:200]}...')
        content = content.strip()

        # Удаляем markdown разметку
        if '```json' in content:
            print('[OpenRouter] Found ```json markdown, extracting...')
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            print('[OpenRouter] Found ``` markdown, extracting...')
            content = content.split('```')[1].split('```')[0].strip()

        try:
            insights = json.loads(content)
            print(f'[OpenRouter] Parsed JSON: {insights}')

            if isinstance(insights, list) and len(insights) > 0:
                # Валидируем структуру
                valid_insights = []
                for insight in insights:
                    if isinstance(insight, dict) and all(k in insight for k in ['category', 'insight', 'type']):
                        valid_insights.append(insight)
                    else:
                        print(f'[OpenRouter] Invalid insight structure: {insight}')

                if valid_insights:
                    print(f'[OpenRouter] Returning {len(valid_insights)} valid insights')
                    return valid_insights
                else:
                    print('[OpenRouter] No valid insights found in response')
        except json.JSONDecodeError as e:
            print(f'[OpenRouter] JSON decode error: {e}')
            print(f'[OpenRouter] Content that failed to parse: {content}')

        return self._get_fallback_insights(data)
    
    def _get_fallback_insights(self, data: Dict[str, Any], error_message: str = None) -> List[Dict[str, str]]:
        """Базовые рекомендации если API недоступен."""
        insights = []

        # Если есть ошибка - показываем её
        if error_message:
            insights.append({
                'category': 'Ошибка подключения',
                'insight': error_message,
                'type': 'warning'
            })
        else:
            # Если API недоступен, возвращаем пустой список
            # Фронтенд покажет сообщение "Нет данных для анализа"
            pass

        return insights[:5]

    def _normalize_insights(self, insights: List[Dict[str, str]], data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Нормализует рекомендации: применяет строгую структуру по типам.
        
        Правила:
        - Максимум 1 success (только если есть реальные достижения)
        - 1-2 warning (проблемы)
        - 1-2 info (нейтральные советы)
        """
        if not insights:
            return []
        
        # Разделяем по типам
        success_insights = [i for i in insights if i.get('type') == 'success']
        warning_insights = [i for i in insights if i.get('type') == 'warning']
        info_insights = [i for i in insights if i.get('type') == 'info']
        
        # Проверяем можно ли вообще хвалить пользователя
        can_praise = self._can_praise_user(data)
        print(f'[OpenRouter] Can praise user: {can_praise}')
        
        normalized = []
        
        # Добавляем success ТОЛЬКО если можно хвалить
        if can_praise and success_insights:
            # Берём максимум 1 success рекомендацию
            normalized.append(success_insights[0])
            print('[OpenRouter] Added 1 success insight (user deserves praise)')
        elif success_insights and not can_praise:
            # Если ИИ добавил success но пользователя нельзя хвалить — конвертируем в info
            converted = success_insights[0].copy()
            converted['type'] = 'info'
            normalized.append(converted)
            print('[OpenRouter] Converted success to info (user should not be praised)')
        
        # Добавляем 1-2 warning
        for i, insight in enumerate(warning_insights[:2]):
            normalized.append(insight)
        print(f'[OpenRouter] Added {min(len(warning_insights), 2)} warning insights')
        
        # Добавляем 1-2 info
        # Если уже есть success, добавляем 1 info, иначе 2
        max_info = 1 if can_praise and success_insights else 2
        for i, insight in enumerate(info_insights[:max_info]):
            normalized.append(insight)
        print(f'[OpenRouter] Added {min(len(info_insights), max_info)} info insights')
        
        return normalized
    
    def _can_praise_user(self, data: Dict[str, Any]) -> bool:
        """
        Проверяет, заслуживает ли пользователь похвалы.
        
        Критерии для похвалы (должен выполняться хотя бы один):
        - Положительный баланс (доходы > расходов)
        - Сбережения > 20% от дохода
        - Есть разнообразие категорий (>3)
        - Регулярные доходы (>1 транзакции)
        
        Запрет на похвалу (если выполняется хотя бы один):
        - Расходы > доходов (отрицательный баланс)
        - "Глупые" траты: рестораны/развлечения > 30% расходов
        - Мало транзакций (<3)
        """
        total_expenses = data.get('total_expenses', 0)
        total_income = data.get('total_income', 0)
        balance = data.get('balance', 0)
        expense_count = data.get('expense_count', 0)
        income_count = data.get('income_count', 0)
        top_categories = data.get('top_categories', [])
        
        # ЗАПРЕТ НА ПОХВАЛУ
        
        # Отрицательный баланс
        if balance < 0:
            print('[OpenRouter] No praise: negative balance')
            return False
        
        # Мало транзакций для анализа
        if expense_count < 3:
            print('[OpenRouter] No praise: too few transactions')
            return False
        
        # Проверяем "глупые" траты (рестораны, развлечения > 30%)
        silly_keywords = ['ресторан', 'кафе', 'развлечен', 'бар', 'кофейн', 'фастфуд', 'доставк', 'еду']
        for cat in top_categories[:2]:  # Проверяем топ-2 категории
            cat_name = cat.get('name', '').lower()
            cat_total = cat.get('total', 0)
            
            if total_expenses > 0:
                share = (cat_total / total_expenses) * 100
                if share > 30:
                    for keyword in silly_keywords:
                        if keyword in cat_name:
                            print(f'[OpenRouter] No praise: silly spending >30% ({cat_name})')
                            return False
        
        # КРИТЕРИИ ДЛЯ ПОХВАЛЫ
        
        # Положительный баланс и сбережения > 20%
        if total_income > 0:
            savings_rate = (balance / total_income) * 100
            if savings_rate >= 20:
                print(f'[OpenRouter] Praise: savings rate {savings_rate:.1f}%')
                return True
        
        # Разнообразие категорий (>3)
        if len(top_categories) >= 3:
            print('[OpenRouter] Praise: diverse categories')
            return True
        
        # Регулярные доходы (>1)
        if income_count > 1:
            print('[OpenRouter] Praise: regular income')
            return True
        
        # Положительный баланс (даже если сбережения < 20%)
        if balance > 0:
            print('[OpenRouter] Praise: positive balance')
            return True
        
        print('[OpenRouter] No praise: no positive criteria met')
        return False


# Singleton instance
openrouter_service = OpenRouterService()
