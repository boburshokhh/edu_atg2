# Инструкция по деплою Django бэкенда

## Структура на сервере

```
~/edu_portal/
├── backend/          # Django бэкенд (git clone)
├── frontend/         # Frontend
├── data/            # Данные для PostgreSQL и MinIO
│   ├── postgres/
│   └── minio/
└── docker-compose.yml
```

## Шаги деплоя

### 1. Обновить docker-compose.yml

Добавьте следующий блок в ваш существующий `docker-compose.yml` файл:

```yaml
backend:
  build:
    context: ./backend
    dockerfile: docker/Dockerfile
  container_name: edu_backend
  restart: always
  depends_on:
    - postgres
  environment:
    # PostgreSQL
    POSTGRES_HOST: postgres
    POSTGRES_PORT: 5432
    POSTGRES_DB: atg_edu
    POSTGRES_USER: admin
    POSTGRES_PASSWORD: 1602atgbobur
    # MinIO
    MINIO_ENDPOINT: http://minio:9000
    MINIO_ACCESS_KEY: admin
    MINIO_SECRET_KEY: 1602atgbobur
    MINIO_BUCKET: atgedu
    # Django
    DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:-change-me-in-production}
    DJANGO_DEBUG: 0
    DJANGO_ALLOWED_HOSTS: localhost,127.0.0.1,0.0.0.0
    CORS_ORIGINS: *
    # JWT
    JWT_ACCESS_SECRET: ${JWT_ACCESS_SECRET:-change-me}
    JWT_REFRESH_SECRET: ${JWT_REFRESH_SECRET:-change-me}
    # Timezone
    TZ: UTC
  ports:
    - "8000:8000"
  networks:
    - edu_network
```

### 2. Настройка переменных окружения

**Важно:** Замените значения по умолчанию для секретных ключей!

Создайте файл `.env` в директории `~/edu_portal/` или установите переменные окружения:

```bash
export DJANGO_SECRET_KEY="ваш-секретный-ключ-для-django"
export JWT_ACCESS_SECRET="ваш-секретный-ключ-для-access-token"
export JWT_REFRESH_SECRET="ваш-секретный-ключ-для-refresh-token"
```

Или добавьте их напрямую в `docker-compose.yml` вместо `${DJANGO_SECRET_KEY:-...}`.

### 3. Проверка схемы базы данных

Убедитесь, что файл `migrations/complete_database_schema.sql` существует в репозитории. 
Команда `bootstrap_db` автоматически выполнится при первом запуске контейнера.

### 4. Создание MinIO bucket

Убедитесь, что bucket `atgedu` создан в MinIO. Вы можете сделать это через веб-консоль MinIO (http://your-server:9001) или через API.

### 5. Запуск

```bash
cd ~/edu_portal
docker-compose up -d --build backend
```

Или для пересборки всех сервисов:

```bash
docker-compose up -d --build
```

### 6. Проверка логов

```bash
docker-compose logs -f backend
```

### 7. Проверка работы

После запуска бэкенд должен быть доступен по адресу:
- `http://your-server-ip:8000`

## Дополнительные SQL миграции

Если у вас есть дополнительные SQL миграции (например, `create_station_extras.sql`), их нужно выполнить вручную:

```bash
docker-compose exec backend python manage.py shell
```

## Troubleshooting

### Проблема: "Postgres not ready"
- Убедитесь, что PostgreSQL контейнер запущен: `docker-compose ps`
- Проверьте логи PostgreSQL: `docker-compose logs postgres`

### Проблема: "Bootstrap failed"
- Проверьте, что файл `migrations/complete_database_schema.sql` существует
- Проверьте логи: `docker-compose logs backend`
- Выполните bootstrap вручную: `docker-compose exec backend python manage.py bootstrap_db`

### Проблема: Не может подключиться к MinIO
- Убедитесь, что MinIO контейнер запущен
- Проверьте, что `MINIO_ENDPOINT` указывает на `http://minio:9000` (имя сервиса, не IP)
- Убедитесь, что оба контейнера в одной сети `edu_network`

### Проблема: CORS ошибки
- Проверьте настройку `CORS_ORIGINS` в docker-compose.yml
- Убедитесь, что `DJANGO_ALLOWED_HOSTS` содержит правильные хосты





