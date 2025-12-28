#!/bin/bash
# Скрипт для диагностики проблемы 502 Bad Gateway на Ubuntu сервере

set -e

echo "=========================================="
echo "Диагностика 502 Bad Gateway на сервере"
echo "=========================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода успеха
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функция для вывода ошибки
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция для вывода предупреждения
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "=== 1. Проверка статуса контейнеров ==="
if docker-compose ps | grep -q "Up"; then
    docker-compose ps
    success "Контейнеры запущены"
else
    error "Некоторые контейнеры не запущены!"
    docker-compose ps
fi

echo ""
echo "=== 2. Проверка логов backend (последние 50 строк) ==="
BACKEND_LOGS=$(docker-compose logs --tail=50 backend 2>&1)
echo "$BACKEND_LOGS"

# Проверка на ошибки в логах
if echo "$BACKEND_LOGS" | grep -qi "error\|exception\|traceback\|failed"; then
    error "Обнаружены ошибки в логах backend!"
    echo "$BACKEND_LOGS" | grep -i "error\|exception\|traceback" | tail -10
fi

# Проверка на успешный запуск Gunicorn
if echo "$BACKEND_LOGS" | grep -qi "Starting Gunicorn\|Booting worker"; then
    success "Gunicorn запущен"
else
    warning "Gunicorn может быть не запущен"
fi

echo ""
echo "=== 3. Проверка доступности backend изнутри frontend ==="
if docker-compose exec -T frontend wget -q -O- http://backend:8000/health 2>&1 | grep -q "ok"; then
    success "Backend доступен из frontend контейнера"
    docker-compose exec -T frontend wget -q -O- http://backend:8000/health
else
    error "Backend НЕ доступен из frontend контейнера!"
    docker-compose exec -T frontend wget -q -O- http://backend:8000/health 2>&1 || true
fi

echo ""
echo "=== 4. Проверка health endpoint напрямую ==="
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    success "Backend доступен на localhost:8000"
    curl -s http://localhost:8000/health
    echo ""
else
    error "Backend НЕ доступен на localhost:8000"
fi

echo ""
echo "=== 5. Проверка health endpoint через nginx ==="
if curl -s -f http://localhost:3000/api/health > /dev/null 2>&1; then
    success "Backend доступен через nginx"
    curl -s http://localhost:3000/api/health
    echo ""
else
    error "Backend НЕ доступен через nginx (502 Bad Gateway)"
    curl -s http://localhost:3000/api/health 2>&1 || true
fi

echo ""
echo "=== 6. Проверка наличия .env файла ==="
if [ -f "backend_django/.env" ]; then
    success "Файл backend_django/.env существует"
else
    error "Файл backend_django/.env НЕ существует!"
    warning "Создайте его: cp backend_django/env.txt backend_django/.env"
fi

echo ""
echo "=== 7. Проверка переменных окружения PostgreSQL ==="
POSTGRES_VARS=$(docker-compose exec -T backend env 2>/dev/null | grep POSTGRES || echo "")
if [ -n "$POSTGRES_VARS" ]; then
    echo "$POSTGRES_VARS"
else
    warning "Переменные POSTGRES не найдены"
fi

echo ""
echo "=== 8. Проверка подключения к PostgreSQL ==="
if docker-compose exec -T backend python -c "
import os
import sys
try:
    import psycopg
    c = psycopg.connect(
        host=os.getenv('POSTGRES_HOST', 'postgres'),
        port=int(os.getenv('POSTGRES_PORT', '5432')),
        dbname=os.getenv('POSTGRES_DB', 'atg_edu'),
        user=os.getenv('POSTGRES_USER', 'admin'),
        password=os.getenv('POSTGRES_PASSWORD', '1602atgbobur'),
        connect_timeout=3
    )
    print('✅ Подключение к PostgreSQL успешно')
    c.close()
except Exception as e:
    print(f'❌ Ошибка подключения к PostgreSQL: {e}')
    sys.exit(1)
" 2>&1; then
    success "PostgreSQL доступен"
else
    error "Ошибка подключения к PostgreSQL"
fi

echo ""
echo "=== 9. Проверка переменных окружения MinIO ==="
MINIO_VARS=$(docker-compose exec -T backend env 2>/dev/null | grep MINIO || echo "")
if [ -n "$MINIO_VARS" ]; then
    echo "$MINIO_VARS" | head -5
else
    warning "Переменные MINIO не найдены"
fi

echo ""
echo "=== 10. Проверка LDAP (если включен) ==="
LDAP_ENABLED=$(docker-compose exec -T backend env 2>/dev/null | grep LDAP_ENABLED | cut -d'=' -f2 || echo "false")
if [ "$LDAP_ENABLED" = "true" ] || [ "$LDAP_ENABLED" = "True" ] || [ "$LDAP_ENABLED" = "1" ]; then
    warning "LDAP включен - проверяю доступность"
    LDAP_SERVER=$(docker-compose exec -T backend env 2>/dev/null | grep LDAP_SERVER | cut -d'=' -f2 | sed 's|ldap://||' | cut -d':' -f1 || echo "")
    if [ -n "$LDAP_SERVER" ]; then
        echo "LDAP сервер: $LDAP_SERVER"
        if docker-compose exec -T backend timeout 5 bash -c "cat < /dev/null > /dev/tcp/$LDAP_SERVER/389" 2>/dev/null; then
            success "LDAP порт доступен"
        else
            error "LDAP порт НЕ доступен - это может быть причиной 502!"
            warning "Временно отключите LDAP: LDAP_ENABLED=false в backend_django/.env"
        fi
    fi
else
    success "LDAP отключен"
fi

echo ""
echo "=== 11. Проверка, что backend слушает на порту 8000 ==="
if docker-compose exec -T backend netstat -tlnp 2>/dev/null | grep -q ":8000" || \
   docker-compose exec -T backend ss -tlnp 2>/dev/null | grep -q ":8000"; then
    success "Backend слушает на порту 8000"
    docker-compose exec -T backend netstat -tlnp 2>/dev/null | grep ":8000" || \
    docker-compose exec -T backend ss -tlnp 2>/dev/null | grep ":8000"
else
    error "Backend НЕ слушает на порту 8000!"
fi

echo ""
echo "=== 12. Проверка использования ресурсов ==="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | head -6 || warning "Не удалось получить статистику"

echo ""
echo "=========================================="
echo "Диагностика завершена"
echo "=========================================="
echo ""
echo "Следующие шаги:"
echo "1. Если backend недоступен - проверьте логи: docker-compose logs backend"
echo "2. Если LDAP недоступен - отключите его временно в backend_django/.env"
echo "3. Если проблема сохраняется - перезапустите: docker-compose restart backend"
echo "4. Для детального анализа экспортируйте логи: docker-compose logs > logs.txt"

