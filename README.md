# Ks Financial App

**Система учёта и анализа персональных финансов с AI-аналитикой**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)

---

## Старт с Docker

```bash
# Сборка и запуск
docker compose build
docker compose up -d

# Проверка статуса
docker compose ps

# Создание суперпользователя
docker compose exec backend python manage.py createsuperuser
```

### Приложение доступно по:
- **Frontend:** http://localhost:80
- **Backend API:** http://localhost:8000

---

## Требования

- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ RAM (рекомендуется 4GB)
- 5GB+ свободного места на диске

---

## Конфигурация (.env)

Создайте файл `.env` в корне проекта:

```bash
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database
POSTGRES_DB=fin_db
POSTGRES_USER=fin_user
POSTGRES_PASSWORD=your-secure-password

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com
FRONTEND_URL=https://your-domain.com

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AI (OpenRouter)
OPENROUTER_API_KEY=your-api-key-here
```

---

## Управление

### Запуск
```bash
docker compose up -d
```

### Остановка
```bash
docker compose down
```

### Перезапуск
```bash
docker compose restart
```

### Логи
```bash
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
```

### Создание суперпользователя
```bash
docker compose exec backend python manage.py createsuperuser
```

### Применение миграций
```bash
docker compose exec backend python manage.py migrate
```

### Бэкап БД
```bash
docker compose exec postgres pg_dump -U fin_user fin_db > backup.sql
```

### Восстановление БД
```bash
docker compose exec -T postgres psql -U fin_user -d fin_db < backup.sql
```

---

## Лицензия

MIT License — см. файл [LICENSE](LICENSE)

