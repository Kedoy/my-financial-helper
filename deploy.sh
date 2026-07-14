#!/bin/bash

# Ks Financial App - Deployment Script
# Автоматическое развёртывание приложения

set -e

echo "=========================================="
echo "  Ks Financial App - Deployment Script  "
echo "=========================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не найден! Установите Docker.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не найден! Установите Docker Compose.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker найден: $(docker --version)"
echo -e "${GREEN}✓${NC} Docker Compose найден: $(docker-compose --version)"
echo ""

# Остановка старых контейнеров
echo -e "${YELLOW}📦 Остановка старых контейнеров...${NC}"
docker-compose down 2>/dev/null || true

# Очистка старых образов (опционально)
if [ "$1" == "--clean" ]; then
    echo -e "${YELLOW}🧹 Очистка старых образов Docker...${NC}"
    docker system prune -f
fi

# Сборка образов
echo -e "${YELLOW}🔨 Сборка Docker образов...${NC}"
echo "   Это может занять несколько минут (загрузка базовых образов и установка зависимостей)"
docker-compose build --no-cache

# Запуск сервисов
echo -e "${YELLOW}🚀 Запуск сервисов...${NC}"
docker-compose up -d

# Ожидание запуска
echo ""
echo -e "${YELLOW}⏳ Ожидание запуска сервисов...${NC}"
sleep 10

# Проверка статуса
echo ""
echo -e "${YELLOW}📊 Статус сервисов:${NC}"
docker-compose ps

# Проверка логов на ошибки
echo ""
echo -e "${YELLOW}📋 Последние логи backend:${NC}"
docker-compose logs --tail=20 backend || true

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Развёртывание завершено!${NC}"
echo "=========================================="
echo ""
echo "📍 Приложение доступно:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs/"
echo ""
echo "📍 Команды управления:"
echo "   Остановить: docker-compose down"
echo "   Перезапустить: docker-compose restart"
echo "   Посмотреть логи: docker-compose logs -f"
echo "   Остановить и очистить: docker-compose down -v"
echo ""
echo "📍 Создание суперпользователя:"
echo "   docker-compose exec backend python manage.py createsuperuser"
echo ""
