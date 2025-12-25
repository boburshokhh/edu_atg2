# Инструкция по исправлению LDAP на сервере

## Проблема
- Docker-compose ожидает файл `backend_django/.env`, но его нет
- Изменения в коде не применены в контейнере
- LDAP настройки могут быть неправильными

## Решение

### 1. Создайте файл .env на сервере

На сервере выполните:

```bash
cd ~/edu_atg
cp backend_django/env.txt backend_django/.env
```

Или создайте файл вручную:

```bash
cat > backend_django/.env << 'EOF'
# Backend env for Docker Compose
# Django
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=change-me
DJANGO_ALLOWED_HOSTS=*
CORS_ORIGINS=*

# JWT
JWT_ACCESS_SECRET=change-me-access
JWT_REFRESH_SECRET=change-me-refresh
ACCESS_TTL_SEC=900
REFRESH_TTL_SEC=1209600

# Postgres (inside Docker network)
POSTGRES_DB=atg_edu
POSTGRES_USER=admin
POSTGRES_PASSWORD=1602atgbobur
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis (inside Docker network)
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO (inside Docker network)
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET=atgedu
MINIO_SECRET_KEY=1602atgbobur
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=1602atgbobur
MINIO_ACCESS_KEY=admin

# LDAP Authentication
LDAP_ENABLED=true
LDAP_SERVER=ldap://DC03.atg.uz
LDAP_BASE_DN=dc=atg,dc=uz
LDAP_USER_DN=
LDAP_USER_PASSWORD=
LDAP_USER_SEARCH_BASE=dc=atg,dc=uz
LDAP_USER_SEARCH_FILTER=(sAMAccountName={username})
LDAP_GROUP_SEARCH_BASE=dc=atg,dc=uz
LDAP_REQUIRE_GROUP=
LDAP_USE_TLS=false
LDAP_TLS_CA_FILE=
EOF
```

### 2. Убедитесь, что все изменения применены

Проверьте, что в репозитории есть все исправления:

```bash
cd ~/edu_atg
git pull
git status
```

### 3. Пересоберите и перезапустите контейнер

```bash
docker compose down backend
docker compose build backend
docker compose up -d backend
```

### 4. Проверьте логи

```bash
# Проверьте общие логи
docker compose logs --tail=100 backend

# Проверьте только LDAP и аутентификацию
docker compose logs --tail=100 backend | grep -i "ldap\|auth\|error\|login"

# Следите за логами в реальном времени
docker compose logs -f backend
```

### 5. Проверьте настройки внутри контейнера

```bash
# Войдите в контейнер
docker exec -it backend bash

# Проверьте переменные окружения
env | grep LDAP

# Проверьте файл .env
cat /app/.env | grep LDAP

# Выйдите из контейнера
exit
```

### 6. Тестирование

Попробуйте войти через веб-интерфейс:
- URL: http://192.168.32.100:3000/login
- Username: a.kuchkarov@atg.uz
- Password: 1234567

### Возможные проблемы и решения

#### Проблема: "required argument is not an integer"
**Решение:** Убедитесь, что код с исправлениями таймаутов применен. Пересоберите контейнер.

#### Проблема: "Cannot connect to LDAP server"
**Решение:** 
- Проверьте, что `extra_hosts` в docker-compose.yml указывает на правильный IP
- Проверьте доступность LDAP сервера из контейнера:
  ```bash
  docker exec -it backend ping -c 3 DC03.atg.uz
  ```

#### Проблема: "User not found in database"
**Решение:** Это нормально при первом входе. Пользователь должен создаться автоматически после успешной LDAP аутентификации.

#### Проблема: 401 Unauthorized
**Решение:**
1. Проверьте логи на ошибки LDAP
2. Убедитесь, что LDAP_ENABLED=true в .env
3. Проверьте правильность учетных данных
4. Убедитесь, что Base DN правильный (dc=atg,dc=uz)

### Проверка конфигурации LDAP

Выполните в контейнере:

```bash
docker exec -it backend python -c "
import os
from django.conf import settings
import django
django.setup()

print('LDAP_ENABLED:', getattr(settings, 'LDAP_ENABLED', False))
print('LDAP_SERVER:', getattr(settings, 'LDAP_SERVER', ''))
print('LDAP_BASE_DN:', getattr(settings, 'LDAP_BASE_DN', ''))
print('LDAP_USER_SEARCH_BASE:', getattr(settings, 'LDAP_USER_SEARCH_BASE', ''))
print('LDAP_USER_SEARCH_FILTER:', getattr(settings, 'LDAP_USER_SEARCH_FILTER', ''))
print('LDAP_CONNECT_TIMEOUT_SEC:', getattr(settings, 'LDAP_CONNECT_TIMEOUT_SEC', 'not set'))
print('LDAP_RECEIVE_TIMEOUT_SEC:', getattr(settings, 'LDAP_RECEIVE_TIMEOUT_SEC', 'not set'))
"
```

