# Диагностика ошибки 502 Bad Gateway при входе

## Причины ошибки 502 Bad Gateway

Ошибка 502 Bad Gateway означает, что nginx не может получить ответ от backend-сервера (Django/Gunicorn). 

### Возможные причины:

1. **Backend контейнер не запущен или упал**
2. **Backend не может подключиться к базе данных (PostgreSQL)**
3. **Backend не может подключиться к MinIO**
4. **Отсутствует файл `.env` с переменными окружения**
5. **Проблемы с сетью между frontend и backend контейнерами**
6. **Backend падает при старте из-за ошибок в коде**

## Шаги диагностики

### 1. Проверьте статус контейнеров

```bash
docker-compose ps
```

Все контейнеры должны быть в статусе `Up`. Если `backend` не запущен или перезапускается, это проблема.

### 2. Проверьте логи backend контейнера

```bash
docker-compose logs backend
```

Ищите ошибки:
- Ошибки подключения к PostgreSQL
- Ошибки подключения к MinIO
- Ошибки миграций
- Ошибки импорта модулей
- Ошибки LDAP (если включен)

### 3. Проверьте логи frontend (nginx) контейнера

```bash
docker-compose logs frontend
```

Ищите ошибки подключения к `http://backend:8000`.

### 4. Проверьте доступность backend изнутри frontend контейнера

```bash
docker-compose exec frontend wget -O- http://backend:8000/health
```

Должен вернуться `{"ok": true}`. Если нет - проблема с сетью или backend не отвечает.

### 5. Проверьте, что backend слушает на порту 8000

```bash
docker-compose exec backend netstat -tlnp | grep 8000
```

Или:

```bash
docker-compose exec backend curl http://localhost:8000/health
```

### 6. Проверьте наличие файла `.env`

```bash
ls -la backend_django/.env
```

Если файла нет, создайте его на основе `env.txt`:

```bash
cp backend_django/env.txt backend_django/.env
```

### 7. Проверьте переменные окружения в backend контейнере

```bash
docker-compose exec backend env | grep POSTGRES
docker-compose exec backend env | grep MINIO
```

## Частые проблемы и решения

### Проблема 1: Backend контейнер постоянно перезапускается

**Причина:** Ошибка в entrypoint.sh или отсутствие зависимостей.

**Решение:**
1. Проверьте логи: `docker-compose logs backend`
2. Убедитесь, что файл `backend_django/.env` существует
3. Проверьте, что PostgreSQL доступен: `docker-compose exec backend python -c "import psycopg; psycopg.connect('host=postgres port=5432 dbname=atg_edu user=admin password=1602atgbobur')"`

### Проблема 2: Backend не может подключиться к PostgreSQL

**Причина:** Неправильные credentials или PostgreSQL еще не готов.

**Решение:**
1. Проверьте переменные в `backend_django/.env`:
   ```
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_DB=atg_edu
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=1602atgbobur
   ```
2. Проверьте, что PostgreSQL запущен: `docker-compose ps postgres`
3. Проверьте логи PostgreSQL: `docker-compose logs postgres`

### Проблема 3: Backend не может подключиться к MinIO

**Причина:** Неправильные credentials или MinIO еще не готов.

**Решение:**
1. Проверьте переменные в `backend_django/.env`:
   ```
   MINIO_ENDPOINT=http://minio:9000
   MINIO_BUCKET=atgedu
   MINIO_ACCESS_KEY=admin
   MINIO_SECRET_KEY=1602atgbobur
   ```
2. Проверьте, что MinIO запущен: `docker-compose ps minio`
3. Проверьте логи MinIO: `docker-compose logs minio`

### Проблема 4: Nginx не может найти backend

**Причина:** Проблемы с Docker сетью или backend не слушает на 0.0.0.0:8000.

**Решение:**
1. Убедитесь, что оба контейнера в одной сети: `docker network inspect edu_atg_default`
2. Проверьте, что backend слушает на 0.0.0.0:8000 (не на 127.0.0.1)
3. Проверьте DNS резолюцию: `docker-compose exec frontend nslookup backend`

### Проблема 5: LDAP таймауты блокируют вход

**Причина:** LDAP сервер недоступен или медленно отвечает.

**Решение:**
1. Временно отключите LDAP в `backend_django/.env`:
   ```
   LDAP_ENABLED=false
   ```
2. Или увеличьте таймауты:
   ```
   LDAP_CONNECT_TIMEOUT_SEC=30
   LDAP_RECEIVE_TIMEOUT_SEC=30
   LDAP_SEARCH_TIME_LIMIT_SEC=30
   ```

## Быстрое решение

Если нужно быстро восстановить работу:

1. **Создайте файл `.env` если его нет:**
   ```bash
   cp backend_django/env.txt backend_django/.env
   ```

2. **Перезапустите все контейнеры:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. **Проверьте логи:**
   ```bash
   docker-compose logs -f backend
   ```

4. **Проверьте health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

5. **Проверьте через nginx:**
   ```bash
   curl http://localhost:3000/api/health
   ```

## Проверка после исправления

После исправления проблем проверьте:

1. ✅ Все контейнеры запущены: `docker-compose ps`
2. ✅ Backend отвечает: `curl http://localhost:8000/health`
3. ✅ Nginx проксирует запросы: `curl http://localhost:3000/api/health`
4. ✅ Логин работает: попробуйте войти через веб-интерфейс

