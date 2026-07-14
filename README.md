# Ks Financial App

**Система учёта и анализа персональных финансов с AI-аналитикой**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)

---

## 🚀 Быстрый старт с Docker

### На сервере (production):

```bash
# 1. Клонировать репозиторий
git clone https://github.com/avekedoy/Ks_Financial-App.git
cd Ks_Financial-App

# 2. Запустить (автоматически установит Docker если нужно)
./start.sh
```

### Вручную:

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
- **API Docs:** http://localhost:8000/api/docs/

---

## 📋 Требования

- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ RAM (рекомендуется 4GB)
- 5GB+ свободного места на диске

---

## 🔧 Конфигурация (.env)

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

## 🛠️ Управление

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

## 📊 Архитектура

```
                    ┌─────────────────┐
                    │   Nginx (80)    │
                    │  Reverse Proxy  │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
     ┌────────▼────────┐          ┌────────▼────────┐
     │  React (80)     │          │  Gunicorn       │
     │  Frontend       │          │  Backend (8000) │
     └─────────────────┘          └────────┬────────┘
                                           │
                          ┌────────────────┴────────────────┐
                          │                                 │
                 ┌────────▼────────┐              ┌────────▼────────┐
                 │  PostgreSQL     │              │     Redis       │
                 │  (5432)         │              │     (6379)      │
                 └─────────────────┘              └─────────────────┘
```

---

## 🧪 Тестирование

### Проверка статуса
```bash
docker compose ps
```

### Проверка backend
```bash
curl http://localhost:8000/api/health/
```

### Проверка frontend
```bash
curl http://localhost:80
```

### API документация
```bash
curl http://localhost:8000/api/docs/
```

---

## 🐛 Troubleshooting

### Ошибка "port already allocated"
```bash
# Найти и остановить конфликтующие процессы
docker compose down
```

### Ошибка подключения к БД
```bash
# Проверить логи
docker compose logs postgres
docker compose logs backend

# Пересоздать БД
docker compose down -v
docker compose up -d postgres
sleep 5
docker compose up -d backend
```

### Frontend не загружается
```bash
# Пересобрать frontend
docker compose build frontend
docker compose up -d frontend
```

### Backend не запускается
```bash
# Проверить логи
docker compose logs backend

# Применить миграции вручную
docker compose exec backend python manage.py migrate
```

### Мало памяти при сборке
```bash
# Добавить swap 2GB
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 🔄 Обновление

```bash
# Получить обновления
git pull

# Пересобрать и перезапустить
docker compose build
docker compose up -d
```

---

## 📦 Volumes

| Volume | Описание |
|--------|----------|
| `postgres_data` | Данные PostgreSQL |
| `backend_static` | Статические файлы Django |
| `backend_media` | Загруженные медиа файлы |

Для очистки всех данных:
```bash
docker compose down -v
```

---

## 🔒 Production Checklist

- [ ] Смените `SECRET_KEY` на случайную строку
- [ ] Установите `DEBUG=False`
- [ ] Смените пароли БД на сложные
- [ ] Настройте `ALLOWED_HOSTS` на ваш домен
- [ ] Настройте HTTPS (SSL сертификаты)
- [ ] Настройте бэкапы PostgreSQL
- [ ] Настройте мониторинг и логирование

---

## 📄 Лицензия

MIT License — см. файл [LICENSE](LICENSE)

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker compose logs -f`
2. Проверьте статус: `docker compose ps`
3. Убедитесь, что все переменные окружения настроены

📖 **Подробная инструкция:** см. [DEPLOYMENT.md](DEPLOYMENT.md)
