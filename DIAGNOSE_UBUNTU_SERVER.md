# Диагностика 502 Bad Gateway на Ubuntu сервере

## Быстрая диагностика на Ubuntu сервере

### 1. Подключитесь к серверу по SSH

```bash
ssh user@192.168.32.100
# или
ssh user@192.168.32.100 -p 22
```

### 2. Перейдите в директорию проекта

```bash
cd /path/to/edu_atg
# или где у вас находится проект
```

### 3. Проверьте статус всех контейнеров

```bash
docker-compose ps
```

**Ожидаемый результат:** Все контейнеры должны быть в статусе `Up`. Если `backend` не запущен или постоянно перезапускается - это проблема.

### 4. Проверьте логи backend (самое важное!)

```bash
# Последние 100 строк логов
docker-compose logs --tail=100 backend

# Логи в реальном времени (нажмите Ctrl+C для выхода)
docker-compose logs -f backend

# Логи только с ошибками
docker-compose logs backend 2>&1 | grep -i error

# Логи за последние 5 минут
docker-compose logs --since 5m backend
```

**Что искать в логах:**
- `[LDAP]` - проблемы с LDAP аутентификацией
- `Postgres is up` - успешное подключение к БД
- `Bucket exists` или `Bucket created` - успешное подключение к MinIO
- `Starting Gunicorn` - сервер запущен
- `ERROR`, `Exception`, `Traceback` - ошибки
- `Connection refused`, `timeout` - проблемы с подключением

### 5. Проверьте логи nginx (frontend)

```bash
# Последние 50 строк
docker-compose logs --tail=50 frontend

# Логи в реальном времени
docker-compose logs -f frontend

# Поиск ошибок 502
docker-compose logs frontend 2>&1 | grep -i "502\|bad gateway\|upstream"
```

### 6. Проверьте доступность backend изнутри frontend контейнера

```bash
docker-compose exec frontend wget -q -O- http://backend:8000/health
```

**Ожидаемый результат:** `{"ok": true}`

Если ошибка - backend недоступен из frontend контейнера.

### 7. Проверьте health endpoint напрямую

```bash
# Изнутри backend контейнера
docker-compose exec backend curl http://localhost:8000/health

# С хоста (если порт проброшен)
curl http://localhost:8000/health

# Через nginx
curl http://localhost:3000/api/health
```

### 8. Проверьте подключение к PostgreSQL

```bash
docker-compose exec backend python -c "
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
    print('✅ PostgreSQL доступен')
    c.close()
except Exception as e:
    print(f'❌ Ошибка подключения к PostgreSQL: {e}')
    sys.exit(1)
"
```

### 9. Проверьте подключение к MinIO

```bash
docker-compose exec backend python -c "
from apps.files.minio_client import s3_client
from django.conf import settings
import django
import sys
try:
    django.setup()
    client = s3_client()
    client.head_bucket(Bucket=settings.MINIO_BUCKET)
    print('✅ MinIO доступен')
except Exception as e:
    print(f'❌ Ошибка подключения к MinIO: {e}')
    sys.exit(1)
"
```

### 10. Проверьте LDAP подключение (если включен)

```bash
# Проверка доступности LDAP сервера
docker-compose exec backend ping -c 3 DC03.atg.uz

# Проверка порта LDAP
docker-compose exec backend nc -zv DC03.atg.uz 389

# Или через telnet
docker-compose exec backend timeout 5 bash -c 'cat < /dev/null > /dev/tcp/DC03.atg.uz/389' && echo "✅ LDAP порт доступен" || echo "❌ LDAP порт недоступен"
```

### 11. Проверьте переменные окружения backend

```bash
# Все переменные
docker-compose exec backend env

# Только PostgreSQL
docker-compose exec backend env | grep POSTGRES

# Только MinIO
docker-compose exec backend env | grep MINIO

# Только LDAP
docker-compose exec backend env | grep LDAP
```

### 12. Проверьте, что backend слушает на порту 8000

```bash
docker-compose exec backend netstat -tlnp | grep 8000
# или
docker-compose exec backend ss -tlnp | grep 8000
```

**Ожидаемый результат:** `0.0.0.0:8000` или `:::8000`

### 13. Проверьте Docker сеть

```bash
# Список сетей
docker network ls

# Информация о сети проекта
docker network inspect $(docker-compose ps -q | head -1 | xargs docker inspect --format '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' 2>/dev/null || echo "edu_atg_default")

# Или проще
docker network inspect edu_atg_default 2>/dev/null || docker network inspect $(docker-compose config | grep -A 1 "networks:" | tail -1 | awk '{print $1}')
```

### 14. Проверьте использование ресурсов

```bash
# Использование CPU и памяти
docker stats --no-stream

# Использование диска
df -h

# Использование памяти контейнерами
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## Автоматический скрипт диагностики

Создайте файл `check_server.sh` на сервере (см. файл `check_server.sh` в проекте) и запустите:

```bash
chmod +x check_server.sh
./check_server.sh
```

## Частые проблемы и решения

### Проблема 1: Backend контейнер постоянно перезапускается

**Диагностика:**
```bash
docker-compose logs --tail=200 backend | tail -50
```

**Возможные причины:**
- Ошибка подключения к PostgreSQL
- Ошибка подключения к MinIO
- Ошибка в коде приложения
- Отсутствует файл `.env`

**Решение:**
1. Проверьте логи (см. выше)
2. Убедитесь, что файл `backend_django/.env` существует
3. Проверьте подключение к зависимостям (PostgreSQL, MinIO)

### Проблема 2: LDAP таймауты блокируют вход

**Диагностика:**
```bash
docker-compose logs backend | grep -i ldap | tail -20
```

**Решение:**
1. Временно отключите LDAP в `backend_django/.env`:
   ```
   LDAP_ENABLED=false
   ```
2. Перезапустите backend:
   ```bash
   docker-compose restart backend
   ```

### Проблема 3: Backend не отвечает на запросы

**Диагностика:**
```bash
# Проверьте, запущен ли Gunicorn
docker-compose exec backend ps aux | grep gunicorn

# Проверьте порт
docker-compose exec backend netstat -tlnp | grep 8000
```

**Решение:**
1. Перезапустите backend:
   ```bash
   docker-compose restart backend
   ```
2. Если не помогло, пересоберите:
   ```bash
   docker-compose up -d --build backend
   ```

### Проблема 4: Nginx не может подключиться к backend

**Диагностика:**
```bash
# Проверьте доступность из frontend
docker-compose exec frontend wget -q -O- http://backend:8000/health

# Проверьте DNS резолюцию
docker-compose exec frontend nslookup backend
docker-compose exec frontend ping -c 3 backend
```

**Решение:**
1. Убедитесь, что оба контейнера в одной сети
2. Перезапустите оба контейнера:
   ```bash
   docker-compose restart backend frontend
   ```

## Мониторинг в реальном времени

### Следить за логами всех сервисов

```bash
docker-compose logs -f
```

### Следить только за backend и frontend

```bash
docker-compose logs -f backend frontend
```

### Следить за системными ресурсами

```bash
watch -n 2 'docker stats --no-stream'
```

## Экспорт логов для анализа

```bash
# Все логи в файл
docker-compose logs > all_logs.txt 2>&1

# Только ошибки
docker-compose logs 2>&1 | grep -i error > errors.txt

# Логи за последний час
docker-compose logs --since 1h > logs_last_hour.txt 2>&1

# Логи конкретного сервиса
docker-compose logs backend > backend_logs.txt 2>&1
```

## Перезапуск сервисов

```bash
# Перезапустить все
docker-compose restart

# Перезапустить только backend
docker-compose restart backend

# Полная перезагрузка (остановить и запустить)
docker-compose down
docker-compose up -d

# Пересборка и перезапуск
docker-compose up -d --build
```

## Проверка после исправления

После исправления проблем проверьте:

```bash
# 1. Все контейнеры запущены
docker-compose ps

# 2. Backend отвечает
curl http://localhost:8000/health

# 3. Nginx проксирует запросы
curl http://localhost:3000/api/health

# 4. Попробуйте войти через веб-интерфейс
# http://192.168.32.100:3000
```

