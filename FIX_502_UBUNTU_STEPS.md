# Пошаговое исправление 502 Bad Gateway на Ubuntu сервере

## Анализ проблемы

Из логов видно:
1. ✅ **Backend работает локально** - сервер запускается, запросы обрабатываются
2. ⚠️ **LDAP таймауты** - LDAP сервер недоступен, но fallback работает
3. ❌ **502 на Ubuntu** - значит backend контейнер не отвечает или не запущен

## Причины 502 Bad Gateway на Ubuntu

### Наиболее вероятные:

1. **Backend контейнер не запущен или падает** (90% вероятность)
   - Синтаксические ошибки (исправлены)
   - Ошибки подключения к БД
   - Ошибки подключения к MinIO

2. **LDAP таймауты блокируют запросы** (если backend запущен)
   - LDAP сервер недоступен
   - Таймауты слишком большие (15 сек)

3. **Проблемы с сетью между контейнерами**
   - Frontend не может достучаться до backend

## Пошаговое решение

### Шаг 1: Подключитесь к Ubuntu серверу

```bash
ssh user@192.168.32.100
cd /path/to/edu_atg
```

### Шаг 2: Проверьте статус контейнеров

```bash
docker-compose ps
```

**Ожидаемый результат:**
```
NAME       IMAGE                    STATUS
backend    edu_atg-backend          Up
frontend   edu_atg-frontend         Up
postgres   postgres:16-alpine       Up
minio      minio/minio:...         Up
redis      redis:7-alpine           Up
```

**Если backend не Up:**
```bash
# Смотрите логи
docker-compose logs --tail=100 backend

# Перезапустите
docker-compose restart backend

# Если не помогло - пересоберите
docker-compose up -d --build backend
```

### Шаг 3: Проверьте логи backend

```bash
# Последние 100 строк
docker-compose logs --tail=100 backend

# В реальном времени
docker-compose logs -f backend
```

**Что искать:**
- ✅ `Starting Gunicorn` - сервер запущен
- ✅ `Postgres is up` - БД доступна
- ✅ `Bucket exists` - MinIO доступен
- ❌ `IndentationError`, `SyntaxError` - ошибки кода
- ❌ `Connection refused`, `timeout` - проблемы с подключением
- ❌ `ERROR`, `Exception`, `Traceback` - ошибки

### Шаг 4: Если backend падает из-за синтаксических ошибок

**На Windows (где разработка):**
```bash
# 1. Закоммитьте исправления
git add backend_django/apps/accounts/views.py
git commit -m "Fix indentation errors in views.py"
git push
```

**На Ubuntu сервере:**
```bash
# 2. Обновите код
git pull

# 3. Пересоберите backend
docker-compose up -d --build backend

# 4. Проверьте логи
docker-compose logs -f backend
```

### Шаг 5: Если backend падает из-за LDAP таймаутов

**Временно отключите LDAP:**

```bash
# 1. Отредактируйте .env
nano backend_django/.env
# или
vi backend_django/.env

# 2. Измените:
LDAP_ENABLED=false

# 3. Сохраните (Ctrl+O, Enter, Ctrl+X в nano)
# 4. Перезапустите backend
docker-compose restart backend

# 5. Проверьте
docker-compose logs -f backend
```

**Или уменьшите таймауты LDAP:**

```bash
# В backend_django/.env добавьте:
LDAP_CONNECT_TIMEOUT_SEC=5
LDAP_RECEIVE_TIMEOUT_SEC=5
LDAP_SEARCH_TIME_LIMIT_SEC=5
```

### Шаг 6: Проверьте доступность backend

```bash
# Изнутри frontend контейнера
docker-compose exec frontend wget -q -O- http://backend:8000/health

# Должно вернуть: {"ok": true}
```

**Если ошибка:**
```bash
# Проверьте сеть
docker network inspect $(docker-compose ps -q backend | head -1 | xargs docker inspect --format '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}')

# Перезапустите оба контейнера
docker-compose restart backend frontend
```

### Шаг 7: Проверьте подключение к зависимостям

```bash
# PostgreSQL
docker-compose exec backend python -c "
import os, psycopg
c = psycopg.connect(
    host=os.getenv('POSTGRES_HOST', 'postgres'),
    port=5432,
    dbname=os.getenv('POSTGRES_DB', 'atg_edu'),
    user=os.getenv('POSTGRES_USER', 'admin'),
    password=os.getenv('POSTGRES_PASSWORD', '1602atgbobur'),
    connect_timeout=3
)
print('✅ PostgreSQL OK')
c.close()
"

# MinIO
docker-compose exec backend python -c "
from apps.files.minio_client import s3_client
from django.conf import settings
import django
django.setup()
client = s3_client()
client.head_bucket(Bucket=settings.MINIO_BUCKET)
print('✅ MinIO OK')
"
```

### Шаг 8: Проверьте health endpoint

```bash
# Прямой доступ
curl http://localhost:8000/health

# Через nginx
curl http://localhost:3000/api/health

# С удаленного компьютера
curl http://192.168.32.100:3000/api/health
```

**Ожидаемый результат:** `{"ok": true}`

### Шаг 9: Если ничего не помогло - полная перезагрузка

```bash
# 1. Остановите все
docker-compose down

# 2. Проверьте, что порты свободны
netstat -tlnp | grep -E "8000|3000|5432"

# 3. Запустите заново
docker-compose up -d

# 4. Следите за логами
docker-compose logs -f
```

## Быстрое решение (если нужно срочно)

```bash
# 1. Отключите LDAP
echo "LDAP_ENABLED=false" >> backend_django/.env

# 2. Перезапустите backend
docker-compose restart backend

# 3. Проверьте
curl http://localhost:3000/api/health
```

## Мониторинг после исправления

```bash
# Следите за логами в реальном времени
docker-compose logs -f backend frontend

# В другом терминале попробуйте войти
# Смотрите, что появляется в логах
```

## Экспорт логов для анализа

Если проблема сохраняется:

```bash
# Все логи
docker-compose logs > all_logs_$(date +%Y%m%d_%H%M%S).txt 2>&1

# Только ошибки
docker-compose logs 2>&1 | grep -i error > errors_$(date +%Y%m%d_%H%M%S).txt

# Скачайте на Windows для анализа
# На Windows:
scp user@192.168.32.100:/path/to/edu_atg/*_logs.txt ./
```

## Проверка после исправления

После всех исправлений проверьте:

1. ✅ Все контейнеры запущены: `docker-compose ps`
2. ✅ Backend отвечает: `curl http://localhost:8000/health`
3. ✅ Nginx проксирует: `curl http://localhost:3000/api/health`
4. ✅ Вход работает: попробуйте войти через веб-интерфейс

## Частые ошибки и решения

### Ошибка: "IndentationError"
**Решение:** Код уже исправлен, нужно обновить на сервере:
```bash
git pull
docker-compose up -d --build backend
```

### Ошибка: "Connection refused to postgres"
**Решение:** Проверьте, что PostgreSQL запущен:
```bash
docker-compose ps postgres
docker-compose restart postgres
```

### Ошибка: "LDAP timeout"
**Решение:** Отключите LDAP или уменьшите таймауты (см. Шаг 5)

### Ошибка: "502 Bad Gateway" даже после исправлений
**Решение:** Проверьте nginx конфигурацию:
```bash
docker-compose exec frontend nginx -t
docker-compose restart frontend
```

