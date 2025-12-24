# Обновление файлов на сервере

## Проблема
Ошибка при сборке:
```
ERROR [backend 4/9] COPY requirements.txt /app/requirements.txt
ERROR [backend 7/9] COPY ../migrations/ /app/migrations/ 2>/dev/null || true
```

## Причина
На сервере старая версия Dockerfile с неправильными путями.

## Решение

### Вариант 1: Обновить через Git (рекомендуется)

```bash
cd ~/edu_atg
git pull
docker compose build --no-cache backend
docker compose up -d
```

### Вариант 2: Обновить файлы вручную

#### 1. Обновите Dockerfile

```bash
cd ~/edu_atg
nano backend_django/docker/Dockerfile
```

Замените содержимое на:

```dockerfile
# Django Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (only curl for healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY backend_django/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend_django/ /app/

# Copy migrations from repo root (for bootstrap_db)
COPY migrations/ /app/migrations/

# Set permissions for entrypoint script
RUN chmod +x /app/docker/entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint
CMD ["/app/docker/entrypoint.sh"]
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

#### 2. Обновите .dockerignore (если нужно)

```bash
cd ~/edu_atg
nano .dockerignore
```

Убедитесь, что строка с `migrations/` закомментирована или удалена:
```
# Backend (exclude from frontend build)
backend_django/
# migrations/ - НЕ исключаем, нужны для backend build
```

#### 3. Пересоберите

```bash
docker compose build --no-cache backend
docker compose up -d
```

### Вариант 3: Скопировать файлы с вашего компьютера

На вашем компьютере (Windows):

```powershell
# Скопировать обновленные файлы на сервер
scp backend_django/docker/Dockerfile root@edusite:~/edu_atg/backend_django/docker/Dockerfile
scp .dockerignore root@edusite:~/edu_atg/.dockerignore
scp docker-compose.yml root@edusite:~/edu_atg/docker-compose.yml
```

На сервере:

```bash
cd ~/edu_atg
docker compose build --no-cache backend
docker compose up -d
```

## Проверка после обновления

```bash
# 1. Проверьте, что файлы обновлены
cat backend_django/docker/Dockerfile | grep "COPY backend_django/requirements.txt"

# Должно показать:
# COPY backend_django/requirements.txt /app/requirements.txt

# 2. Проверьте структуру
ls -la migrations/
ls -la backend_django/requirements.txt

# 3. Соберите
docker compose build --no-cache backend

# 4. Запустите
docker compose up -d

# 5. Проверьте логи
docker compose logs -f backend
```

## Быстрая команда (если используете git)

```bash
cd ~/edu_atg && \
git pull && \
docker compose build --no-cache backend && \
docker compose up -d && \
docker compose ps
```

