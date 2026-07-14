from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Очистить кэш AI рекомендаций'

    def handle(self, *args, **kwargs):
        self.stdout.write('Очистка кэша AI рекомендаций...')
        
        # Очищаем все ключи с префиксом ai_insights
        cache_key_pattern = 'ai_insights_*'
        deleted_count = 0
        
        # В зависимости от бэкенда кэша
        try:
            # Для file-based cache или memory cache
            from django.core.cache import caches
            default_cache = caches['default']
            
            # Пробуем очистить по паттерну (работает не для всех бэкендов)
            for key in default_cache._cache.keys():
                if key.startswith('ai_insights_'):
                    default_cache.delete(key)
                    deleted_count += 1
        except Exception:
            # Если не получилось по паттерну - очищаем весь кэш
            cache.clear()
            self.stdout.write(self.style.WARNING('Очищен весь кэш'))
        
        self.stdout.write(self.style.SUCCESS(f'Удалено {deleted_count} ключей кэша AI'))
