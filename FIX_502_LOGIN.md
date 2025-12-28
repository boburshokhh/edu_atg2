# Исправление ошибки 502 Bad Gateway при входе

## Анализ проблемы

Ошибка **502 Bad Gateway** при попытке входа означает, что nginx не может получить ответ от backend-сервера Django. 

### Наиболее вероятные причины:

1. **LDAP сервер недоступен или медленно отвечает** ⚠️ **НАИБОЛЕЕ ВЕРОЯТНО**
   - LDAP включен по умолчанию (`LDAP_ENABLED=true`)
   - Сервер `ldap://DC03.atg.uz` может быть недоступен
   - Таймауты LDAP (15 секунд) могут быть недостаточными
   - Если LDAP зависает, весь запрос на вход блокируется

2. **Backend контейнер не запущен или упал**
   - Проверьте: `docker-compose ps`

3. **Backend не может подключиться к PostgreSQL**
   - Проверьте логи: `docker-compose logs backend`

4. **Backend не может подключиться к MinIO**
   - Проверьте логи: `docker-compose logs backend`

## Быстрое решение

### Вариант 1: Временно отключить LDAP (рекомендуется для диагностики)

1. Откройте файл `backend_django/.env`
2. Измените:
   ```
   LDAP_ENABLED=false
   ```
3. Перезапустите backend:
   ```bash
   docker-compose restart backend
   ```
4. Попробуйте войти снова

Если это помогло - проблема в LDAP. Переходите к варианту 2.

### Вариант 2: Увеличить таймауты LDAP

Если LDAP нужен, но сервер медленный:

1. Откройте файл `backend_django/.env`
2. Добавьте/измените:
   ```
   LDAP_CONNECT_TIMEOUT_SEC=30
   LDAP_RECEIVE_TIMEOUT_SEC=30
   LDAP_SEARCH_TIME_LIMIT_SEC=30
   ```
3. Перезапустите backend:
   ```bash
   docker-compose restart backend
   ```

### Вариант 3: Проверить доступность LDAP сервера

Проверьте, доступен ли LDAP сервер из backend контейнера:

```bash
docker-compose exec backend ping -c 3 DC03.atg.uz
```

Или проверьте порт:

```bash
docker-compose exec backend nc -zv DC03.atg.uz 389
```

Если сервер недоступен:
- Проверьте сетевые настройки
- Убедитесь, что IP адрес `192.168.2.7` правильный в `docker-compose.yml`
- Проверьте firewall правила

## Полная диагностика

Запустите скрипт диагностики:

**Windows (PowerShell):**
```powershell
.\check_backend.ps1
```

**Linux/Mac:**
```bash
chmod +x check_backend.sh
./check_backend.sh
```

Или вручную:

### 1. Проверьте статус контейнеров
```bash
docker-compose ps
```

Все должны быть `Up`. Если `backend` перезапускается - смотрите логи.

### 2. Проверьте логи backend
```bash
docker-compose logs --tail=100 backend
```

Ищите:
- `[LDAP]` сообщения - проблемы с LDAP
- `Postgres is up` - успешное подключение к БД
- `Bucket exists` - успешное подключение к MinIO
- `Starting Gunicorn` - сервер запущен
- Ошибки импорта или конфигурации

### 3. Проверьте доступность backend
```bash
# Прямой доступ
curl http://localhost:8000/health

# Через nginx
curl http://localhost:3000/api/health
```

Оба должны вернуть `{"ok": true}`.

### 4. Проверьте подключение к PostgreSQL
```bash
docker-compose exec backend python -c "
import os
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
"
```

### 5. Проверьте подключение к MinIO
```bash
docker-compose exec backend python -c "
from apps.files.minio_client import s3_client
from django.conf import settings
import django
django.setup()
client = s3_client()
client.head_bucket(Bucket=settings.MINIO_BUCKET)
print('✅ MinIO доступен')
"
```

## Изменения в nginx.conf

Я улучшил конфигурацию nginx для лучшей обработки ошибок:

1. **Уменьшены таймауты подключения** - быстрее обнаружит, если backend недоступен
2. **Добавлена обработка ошибок** - возвращает понятное сообщение при 502
3. **Улучшена обработка таймаутов** - не ждет слишком долго

После изменений пересоберите frontend:

```bash
docker-compose build frontend
docker-compose up -d frontend
```

## Рекомендации

1. **Для продакшена:** Настройте мониторинг health endpoint
2. **Для LDAP:** Добавьте fallback на локальную аутентификацию при недоступности LDAP
3. **Для отладки:** Включите подробное логирование в `backend_django/.env`:
   ```
   DJANGO_DEBUG=1
   ```

## Если ничего не помогло

1. Полностью перезапустите все контейнеры:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. Проверьте, что все зависимости запущены:
   ```bash
   docker-compose ps
   ```

3. Проверьте логи всех сервисов:
   ```bash
   docker-compose logs postgres
   docker-compose logs redis
   docker-compose logs minio
   docker-compose logs backend
   docker-compose logs frontend
   ```

4. Проверьте сеть Docker:
   ```bash
   docker network inspect edu_atg_default
   ```

5. Проверьте, что порты не заняты:
   ```bash
   netstat -an | findstr "8000 3000 5432"
   ```

