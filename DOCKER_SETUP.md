# Docker Setup Guide

Полная инструкция по настройке и запуску проекта через Docker.

## Быстрый старт

1. **Скопируйте файл с переменными окружения:**
   ```bash
   cp .env.example .env
   ```

2. **Отредактируйте `.env` файл** и установите свои значения для:
   - `POSTGRES_PASSWORD` - пароль для PostgreSQL
   - `MINIO_ROOT_PASSWORD` - пароль для MinIO
   - `DJANGO_SECRET_KEY` - секретный ключ Django (сгенерируйте случайную строку)
   - `JWT_ACCESS_SECRET` и `JWT_REFRESH_SECRET` - секреты для JWT токенов

3. **Запустите все сервисы:**
   ```bash
   docker compose build
   docker compose up -d
   ```

4. **Проверьте статус:**
   ```bash
   docker compose ps
   ```

## Структура сервисов

### PostgreSQL (порт 5432)
- База данных: `atg`
- Пользователь: `atg`
- Пароль: из переменной `POSTGRES_PASSWORD` в `.env`
- Автоматически создаются расширения и применяется схема БД

### MinIO (порты 9000, 9001)
- API: http://localhost:9000
- Console: http://localhost:9001
- Bucket: `atgedu` (создается автоматически)
- Учетные данные: из переменных `MINIO_ROOT_USER` и `MINIO_ROOT_PASSWORD`

### Django Backend (порт 8000)
- API: http://localhost:8000
- Health check: http://localhost:8000/health
- Автоматически выполняет миграции при запуске
- Запускает bootstrap_db для инициализации данных

### Frontend (порт 3000)
- Приложение: http://localhost:3000
- Nginx проксирует `/api/*` на backend
- Статические файлы обслуживаются напрямую

## Переменные окружения

### Основные переменные (.env)

```bash
# PostgreSQL
POSTGRES_DB=atg
POSTGRES_USER=atg
POSTGRES_PASSWORD=your_secure_password

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_password
MINIO_BUCKET=atgedu

# Django
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# CORS
CORS_ORIGINS=http://localhost:3000

# JWT
JWT_ACCESS_SECRET=your_jwt_access_secret
JWT_REFRESH_SECRET=your_jwt_refresh_secret
```

## Команды управления

### Запуск
```bash
# Запуск в фоновом режиме
docker compose up -d

# Запуск с выводом логов
docker compose up
```

### Остановка
```bash
# Остановка сервисов
docker compose stop

# Остановка и удаление контейнеров
docker compose down

# Остановка с удалением volumes (⚠️ удалит данные!)
docker compose down -v
```

### Логи
```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### Пересборка
```bash
# Пересобрать все образы
docker compose build

# Пересобрать конкретный сервис
docker compose build backend
docker compose build frontend

# Пересобрать и перезапустить
docker compose up -d --build
```

### Выполнение команд в контейнерах
```bash
# Django shell
docker compose exec backend python manage.py shell

# Django migrations
docker compose exec backend python manage.py migrate

# Django createsuperuser (если используется)
docker compose exec backend python manage.py createsuperuser

# Bash в контейнере
docker compose exec backend bash
```

## Health Checks

Все сервисы имеют health checks:
- **PostgreSQL**: проверка готовности через `pg_isready`
- **MinIO**: проверка через HTTP health endpoint
- **Backend**: проверка через `/health` endpoint
- **Frontend**: проверка доступности через `wget`

## Volumes (данные)

Данные сохраняются в Docker volumes:
- `pgdata` - данные PostgreSQL
- `miniodata` - данные MinIO

Для просмотра volumes:
```bash
docker volume ls
```

Для резервного копирования:
```bash
# PostgreSQL
docker-compose exec postgres pg_dump -U atg atg > backup.sql

# MinIO (через mc)
docker-compose exec minio-init /usr/bin/mc mirror local/atgedu /backup
```

## Troubleshooting

### Backend не запускается
1. Проверьте логи: `docker compose logs backend`
2. Убедитесь, что PostgreSQL готов: `docker compose ps postgres`
3. Проверьте переменные окружения в `.env`

### Frontend не подключается к API
1. Проверьте, что backend запущен: `docker compose ps backend`
2. Проверьте health endpoint: `curl http://localhost:8000/health`
3. Проверьте nginx конфигурацию в `nginx.conf`

### MinIO bucket не создается
1. Проверьте логи minio-init: `docker compose logs minio-init`
2. Убедитесь, что переменная `MINIO_BUCKET` установлена
3. Проверьте доступ к MinIO console: http://localhost:9001

### Проблемы с миграциями
```bash
# Выполнить миграции вручную
docker compose exec backend python manage.py migrate

# Откатить миграции (если нужно)
docker compose exec backend python manage.py migrate app_name zero
```

## Production настройки

Для production измените в `.env`:
- `DJANGO_DEBUG=0`
- Установите сильные пароли
- Настройте `DJANGO_ALLOWED_HOSTS` с вашим доменом
- Настройте `CORS_ORIGINS` с вашим фронтенд доменом
- Используйте SSL/TLS для MinIO и PostgreSQL
- Настройте резервное копирование

## Дополнительная информация

- Backend документация: `backend_django/DEPLOYMENT.md`
- Frontend конфигурация: `frontend.env`
- Nginx конфигурация: `nginx.conf`


