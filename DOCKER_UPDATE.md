# Инструкция по обновлению Docker контейнеров

## Быстрое обновление (если изменился только код)

```bash
# 1. Остановить контейнер backend
docker compose stop backend

# 2. Пересобрать образ с новым кодом
docker compose build backend

# 3. Запустить контейнер заново
docker compose up -d backend

# 4. Проверить логи
docker compose logs -f backend
```

## Полное обновление (если изменились зависимости или Dockerfile)

```bash
# 1. Остановить и удалить контейнер
docker compose down backend

# 2. Пересобрать образ без кеша (если нужно)
docker compose build --no-cache backend

# 3. Запустить контейнер
docker compose up -d backend

# 4. Проверить логи
docker compose logs -f backend
```

## Обновление всех сервисов

```bash
# Остановить все контейнеры
docker compose down

# Пересобрать все образы
docker compose build

# Запустить все контейнеры
docker compose up -d

# Проверить статус
docker compose ps

# Проверить логи backend
docker compose logs -f backend
```

## Если изменился только .env файл

```bash
# 1. Убедитесь, что файл .env создан
cp backend_django/env.txt backend_django/.env

# 2. Перезапустите контейнер (без пересборки)
docker compose restart backend

# 3. Проверьте логи
docker compose logs -f backend
```

## Проверка изменений

После перезапуска проверьте:

```bash
# 1. Статус контейнеров
docker compose ps

# 2. Логи backend (последние 50 строк)
docker compose logs --tail=50 backend

# 3. Логи с фильтром по LDAP/аутентификации
docker compose logs --tail=100 backend | grep -i "ldap\|auth\|error\|login"

# 4. Войти в контейнер для проверки (опционально)
docker exec -it backend bash

# Внутри контейнера:
# - Проверить переменные окружения
env | grep LDAP

# - Проверить файлы
ls -la /app/

# - Проверить настройки Django
python manage.py shell
>>> from django.conf import settings
>>> print(settings.LDAP_ENABLED)
>>> print(settings.LDAP_BASE_DN)
```

## Быстрая команда для обновления backend

```bash
# Одной командой: остановить, пересобрать, запустить
docker compose down backend && docker compose build backend && docker compose up -d backend && docker compose logs -f backend
```

## Если контейнер не запускается

```bash
# 1. Проверьте логи ошибок
docker compose logs backend

# 2. Проверьте статус
docker compose ps -a

# 3. Удалите контейнер и пересоздайте
docker compose rm -f backend
docker compose up -d --build backend

# 4. Проверьте образы
docker images | grep edu_atg
```

## Очистка (если нужно)

```bash
# Удалить все контейнеры, сети и volumes (ОСТОРОЖНО!)
docker compose down -v

# Удалить неиспользуемые образы
docker image prune -a

# Полная очистка (удалит все неиспользуемые ресурсы)
docker system prune -a
```

