# Исправление ошибки сборки Docker

## Проблема
```
failed to solve: failed to compute cache key: failed to calculate checksum of ref ... "/migrations": not found
```

## Причина
На сервере отсутствуют необходимые файлы или они в другом месте.

## Решение

### Вариант 1: Проверьте структуру проекта на сервере

```bash
cd ~/edu_atg
ls -la

# Проверьте наличие папок:
ls -la backend_django/
ls -la migrations/
ls -la backend_django/requirements.txt
```

Если папок нет, нужно:
1. Либо скопировать их с вашего компьютера
2. Либо получить через `git pull`

### Вариант 2: Если используете внешние сервисы (PostgreSQL, MinIO)

Если PostgreSQL и MinIO находятся на другом сервере (192.168.32.100), закомментируйте их в docker-compose.yml:

```yaml
services:
  # postgres:
  #   image: postgres:16
  #   ...

  # minio:
  #   image: minio/minio:RELEASE.2024-10-13T13-34-11Z
  #   ...

  backend:
    build:
      context: .
      dockerfile: backend_django/docker/Dockerfile
    # ...
    depends_on:
      # postgres:
      #   condition: service_healthy
      # minio-init:
      #   condition: service_completed_successfully
    environment:
      POSTGRES_HOST: 192.168.32.100  # Внешний сервер
      MINIO_ENDPOINT: http://192.168.32.100:9000  # Внешний сервер
      # ...
```

### Вариант 3: Создайте недостающие файлы/папки

Если папка `migrations/` отсутствует:

```bash
cd ~/edu_atg
mkdir -p migrations
# Скопируйте SQL файлы в migrations/
```

Если папка `backend_django/` отсутствует или неполная:

```bash
cd ~/edu_atg
# Получите код через git
git pull
# или скопируйте вручную
```

### Вариант 4: Временное решение - упрощенный Dockerfile

Если структура проекта на сервере отличается, можно временно изменить Dockerfile:

```dockerfile
# В backend_django/docker/Dockerfile измените:
# Вместо:
COPY migrations/ /app/migrations/

# Используйте (если migrations в другом месте):
# COPY ../migrations/ /app/migrations/ || echo "Migrations not found"
```

Но лучше исправить структуру проекта.

## Проверка после исправления

```bash
# 1. Проверьте структуру
cd ~/edu_atg
tree -L 2 -I 'node_modules|venv|__pycache__'

# 2. Проверьте docker-compose конфигурацию
docker compose config

# 3. Попробуйте собрать снова
docker compose build --no-cache backend

# 4. Если успешно, запустите все
docker compose up -d
```

## Быстрая диагностика

```bash
cd ~/edu_atg

# Проверьте наличие всех нужных файлов
echo "=== Проверка структуры ==="
[ -d backend_django ] && echo "✓ backend_django/ существует" || echo "✗ backend_django/ НЕ существует"
[ -f backend_django/requirements.txt ] && echo "✓ requirements.txt существует" || echo "✗ requirements.txt НЕ существует"
[ -d migrations ] && echo "✓ migrations/ существует" || echo "✗ migrations/ НЕ существует"
[ -f docker-compose.yml ] && echo "✓ docker-compose.yml существует" || echo "✗ docker-compose.yml НЕ существует"

# Проверьте содержимое
echo ""
echo "=== Содержимое backend_django ==="
ls -la backend_django/ | head -10

echo ""
echo "=== Содержимое migrations ==="
ls -la migrations/ 2>/dev/null || echo "Папка migrations не найдена"
```

