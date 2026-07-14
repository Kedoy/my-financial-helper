from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Удаляет всех пользователей кроме admin@admin.com и их данные'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Подтверждение удаления (без этого флага ничего не удалится)',
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        
        # Находим admin пользователя
        try:
            admin_user = User.objects.get(email='admin@admin.com')
            self.stdout.write(f'Найден admin пользователь: {admin_user.email}')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Пользователь admin@admin.com не найден! Создаю...'
            ))
            admin_user = User.objects.create_superuser(
                email='admin@admin.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(
                f'Создан admin пользователь с паролем: admin123'
            ))

        # Получаем всех пользователей кроме admin
        users_to_delete = User.objects.exclude(email='admin@admin.com')
        count = users_to_delete.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                'Нет пользователей для удаления (кроме admin)'
            ))
            return

        self.stdout.write(self.style.WARNING(
            f'Найдено {count} пользователей для удаления:'
        ))
        for user in users_to_delete:
            self.stdout.write(f'  - {user.email} (ID: {user.id})')

        if not confirm:
            self.stdout.write(self.style.WARNING(
                '\nИспользуйте --confirm для подтверждения удаления'
            ))
            return

        # Удаляем пользователей и их данные
        with transaction.atomic():
            for user in users_to_delete:
                # Удаляем транзакции пользователя
                from apps.transactions.models import Transaction
                deleted_count, _ = Transaction.objects.filter(user=user).delete()
                if deleted_count:
                    self.stdout.write(f'  Удалено транзакций у {user.email}: {deleted_count}')

                # Удаляем пользовательские категории (не системные)
                from apps.categories.models import Category
                deleted_count, _ = Category.objects.filter(user=user).delete()
                if deleted_count:
                    self.stdout.write(f'  Удалено категорий у {user.email}: {deleted_count}')

                # Удаляем пользователя
                user.delete()
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Удалён пользователь: {user.email}'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'\nГотово! Удалено {count} пользователей.'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Остался только admin@admin.com'
        ))
