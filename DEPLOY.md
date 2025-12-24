# Инструкция по деплою на сервер

## Подготовка

### 1. Остановить текущие контейнеры

```bash
cd ~/edu_portal
docker compose down
# или
docker-compose down
```

### 2. Сохранить данные

```bash
# Создать бэкап данных
cp -a ~/edu_portal/data ~/edu_data_backup
# или переместить
mv ~/edu_portal/data ~/edu_data_backup
```

### 3. Удалить старую папку и клонировать репозиторий

```bash
# Удалить старую папку
rm -rf ~/edu_portal

# Клонировать репозиторий
git clone https://github.com/boburshokhh/edu_atg2.git ~/edu_atg
cd ~/edu_atg
```

### 4. Вернуть данные

```bash
# Вернуть данные в новую структуру
mv ~/edu_data_backup ~/edu_atg/data
```

### 5. Создать .env файл

Создайте файл `.env` в корне проекта `~/edu_atg/.env`:

```bash
# PostgreSQL
POSTGRES_DB=atg
POSTGRES_USER=atg
POSTGRES_PASSWORD=ваш-пароль

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=ваш-пароль
MINIO_BUCKET=atgedu

# Django
DJANGO_SECRET_KEY=ваш-секретный-ключ
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=*
CORS_ORIGINS=*

# JWT
JWT_ACCESS_SECRET=ваш-секретный-ключ
JWT_REFRESH_SECRET=ваш-секретный-ключ

# Timeouts
ACCESS_TTL_SEC=900
REFRESH_TTL_SEC=1209600
```

**Важно:** Замените все значения по умолчанию на реальные секретные ключи!

### 6. Проверить конфигурацию

```bash
# Проверить синтаксис docker-compose.yml
docker compose config
```

Если есть ошибки, исправьте их перед продолжением.

### 7. Запустить стек

```bash
# Собрать и запустить все сервисы
docker compose up -d --build

# Или запустить по отдельности
docker compose up -d --build postgres redis minio
docker compose up -d --build backend
docker compose up -d --build frontend
```

### 8. Проверить логи

```bash
# Все сервисы
docker compose logs -f

# Отдельный сервис
docker compose logs -f backend
docker compose logs -f frontend
```

### 9. Проверка работы

1. **Фронтенд:** Откройте `http://SERVER_IP:3000` в браузере
2. **API через фронтенд:** Проверьте, что запросы идут на `/api/auth/login` (не на `localhost:8000`)
3. **Прямой доступ к API:** `curl -i http://SERVER_IP:3000/api/auth/login` (должен отвечать, не connection refused)

## Структура проекта на сервере

После деплоя структура должна быть:

```
~/edu_atg/
├── backend_django/       # Django бэкенд
│   └── docker/
│       └── Dockerfile
├── data/                # Данные (Postgres, MinIO)
│   ├── postgres/
│   └── minio/
├── migrations/          # SQL миграции
├── src/                # Frontend исходники
├── Dockerfile.frontend  # Dockerfile для фронтенда
├── nginx.conf          # Конфигурация nginx для фронтенда
├── docker-compose.yml  # Docker Compose конфигурация
└── .env                # Переменные окружения
```

## Troubleshooting

### Проблема: "Cannot find Dockerfile"

Убедитесь, что файлы находятся в правильных местах:
- `backend_django/docker/Dockerfile` - должен существовать
- `Dockerfile.frontend` - должен быть в корне проекта
- `nginx.conf` - должен быть в корне проекта

### Проблема: "Connection refused" при запросах к API

1. Проверьте, что backend контейнер запущен: `docker compose ps`
2. Проверьте логи backend: `docker compose logs backend`
3. Убедитесь, что nginx.conf правильно проксирует на `http://backend:8000`

### Проблема: Данные не сохранились

Если данные не сохранились, проверьте:
1. Что папка `data/` существует в корне проекта
2. Что volumes правильно настроены в docker-compose.yml
3. Что права доступа правильные: `chmod -R 755 data/`

### Проблема: CORS ошибки

Проверьте настройки в `.env`:
- `CORS_ORIGINS=*` (или конкретные домены)
- `DJANGO_ALLOWED_HOSTS=*` (или конкретные хосты)

## Обновление

Для обновления кода:

```bash
cd ~/edu_atg
git pull
docker compose up -d --build
```

Данные в `data/` сохранятся автоматически.

