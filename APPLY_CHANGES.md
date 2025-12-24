# Инструкция по применению изменений Docker на сервере

## Быстрое применение изменений

### 1. Подключитесь к серверу

```bash
ssh root@edusite
# или ваш способ подключения
cd ~/edu_atg
```

### 2. Сохраните текущие данные (опционально, но рекомендуется)

```bash
# Создать бэкап базы данных
docker compose exec postgres pg_dump -U admin atg_edu > backup_$(date +%Y%m%d_%H%M%S).sql

# Или если используете внешний PostgreSQL:
# pg_dump -h 192.168.32.100 -U admin atg_edu > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 3. Получите последние изменения из репозитория

```bash
# Если используете git
git pull origin main
# или
git pull origin master

# Если не используете git, скопируйте обновленный docker-compose.yml вручную
```

### 4. Остановите текущие контейнеры

```bash
docker compose down
```

### 5. Обновите .env файл (если нужно)

Проверьте, что в `.env` файле (в корне проекта) установлены правильные значения:

```bash
cat .env
```

Если нужно обновить, отредактируйте:
```bash
nano .env
```

Убедитесь, что значения соответствуют новым дефолтам в docker-compose.yml:
- `POSTGRES_DB=atg_edu`
- `POSTGRES_USER=admin`
- `POSTGRES_PASSWORD=1602atgbobur`
- `MINIO_ROOT_USER=admin`
- `MINIO_ROOT_PASSWORD=1602atgbobur`
- И т.д.

### 6. Пересоберите и запустите контейнеры

```bash
# Пересобрать образы с нуля (без кеша)
docker compose build --no-cache

# Или если хотите использовать кеш (быстрее):
docker compose build

# Запустить все сервисы
docker compose up -d
```

### 7. Проверьте статус контейнеров

```bash
docker compose ps
```

Все контейнеры должны быть в статусе `Up` и `healthy`.

### 8. Проверьте логи

```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### 9. Проверьте работу приложения

```bash
# Проверка backend health
curl http://localhost:8000/health

# Проверка frontend
curl http://localhost:3000
```

## Если что-то пошло не так

### Откат к предыдущей версии

```bash
# Остановить контейнеры
docker compose down

# Вернуть старый docker-compose.yml (если есть бэкап)
# или через git:
git checkout HEAD~1 docker-compose.yml

# Запустить снова
docker compose up -d
```

### Очистка и полная пересборка

```bash
# Остановить и удалить контейнеры
docker compose down

# Удалить старые образы (опционально)
docker compose down --rmi all

# Очистить неиспользуемые данные Docker (осторожно!)
docker system prune -f

# Пересобрать с нуля
docker compose build --no-cache
docker compose up -d
```

### Проблемы с миграциями базы данных

```bash
# Выполнить миграции вручную
docker compose exec backend python manage.py migrate

# Если нужно откатить
docker compose exec backend python manage.py migrate app_name zero
```

### Проблемы с MinIO bucket

```bash
# Проверить логи minio-init
docker compose logs minio-init

# Создать bucket вручную через MinIO console
# Откройте http://SERVER_IP:9001
# Логин: admin, Пароль: 1602atgbobur
```

## Важные замечания

1. **Данные сохраняются** в Docker volumes (`pgdata`, `miniodata`), поэтому при `docker compose down` данные не удаляются.

2. **Если используете внешние сервисы** (PostgreSQL или MinIO на другом сервере):
   - Закомментируйте соответствующие сервисы в docker-compose.yml
   - Убедитесь, что в `.env` указаны правильные хосты:
     - `POSTGRES_HOST=192.168.32.100`
     - `MINIO_ENDPOINT=http://192.168.32.100:9000`

3. **Пароли в docker-compose.yml**: Теперь дефолтные значения соответствуют вашим реальным, но для безопасности лучше использовать `.env` файл и не коммитить его в git.

## Проверка после обновления

```bash
# 1. Статус всех контейнеров
docker compose ps

# 2. Health checks
docker compose ps | grep healthy

# 3. Логи без ошибок
docker compose logs backend | tail -20

# 4. Доступность API
curl -I http://localhost:8000/health

# 5. Доступность Frontend
curl -I http://localhost:3000
```

## Быстрая команда (все в одном)

```bash
cd ~/edu_atg && \
git pull && \
docker compose down && \
docker compose build && \
docker compose up -d && \
docker compose ps && \
echo "Обновление завершено!"
```

