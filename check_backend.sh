#!/bin/bash
# Скрипт для диагностики проблемы 502 Bad Gateway

echo "=== Проверка статуса контейнеров ==="
docker-compose ps

echo ""
echo "=== Проверка логов backend (последние 50 строк) ==="
docker-compose logs --tail=50 backend

echo ""
echo "=== Проверка доступности backend изнутри frontend ==="
docker-compose exec -T frontend wget -q -O- http://backend:8000/health 2>&1 || echo "ОШИБКА: Backend недоступен из frontend контейнера"

echo ""
echo "=== Проверка health endpoint напрямую ==="
curl -s http://localhost:8000/health || echo "ОШИБКА: Backend недоступен на localhost:8000"

echo ""
echo "=== Проверка health endpoint через nginx ==="
curl -s http://localhost:3000/api/health || echo "ОШИБКА: Backend недоступен через nginx"

echo ""
echo "=== Проверка наличия .env файла ==="
if [ -f "backend_django/.env" ]; then
    echo "✅ Файл backend_django/.env существует"
else
    echo "❌ Файл backend_django/.env НЕ существует!"
    echo "   Создайте его: cp backend_django/env.txt backend_django/.env"
fi

echo ""
echo "=== Проверка переменных окружения PostgreSQL ==="
docker-compose exec -T backend env | grep POSTGRES || echo "Переменные POSTGRES не найдены"

echo ""
echo "=== Проверка переменных окружения MinIO ==="
docker-compose exec -T backend env | grep MINIO || echo "Переменные MINIO не найдены"

echo ""
echo "=== Проверка подключения к PostgreSQL ==="
docker-compose exec -T backend python -c "
import os
import sys
try:
    import psycopg
    host = os.getenv('POSTGRES_HOST', 'postgres')
    port = int(os.getenv('POSTGRES_PORT', '5432'))
    db = os.getenv('POSTGRES_DB', 'atg_edu')
    user = os.getenv('POSTGRES_USER', 'admin')
    pwd = os.getenv('POSTGRES_PASSWORD', 'admin')
    c = psycopg.connect(host=host, port=port, dbname=db, user=user, password=pwd, connect_timeout=3)
    c.close()
    print('✅ Подключение к PostgreSQL успешно')
except Exception as e:
    print(f'❌ Ошибка подключения к PostgreSQL: {e}')
    sys.exit(1)
" || echo "❌ Не удалось проверить подключение к PostgreSQL"

echo ""
echo "=== Диагностика завершена ==="

