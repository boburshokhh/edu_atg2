# Быстрое исправление 502 Bad Gateway

## На Ubuntu сервере (192.168.32.100)

### Шаг 1: Подключитесь к серверу

```bash
ssh user@192.168.32.100
# Замените user на ваше имя пользователя
```

### Шаг 2: Перейдите в директорию проекта

```bash
cd /path/to/edu_atg
# Укажите правильный путь к проекту
```

### Шаг 3: Запустите диагностику

```bash
# Скопируйте скрипт на сервер (если его еще нет)
chmod +x check_server.sh
./check_server.sh
```

Или вручную проверьте:

```bash
# 1. Статус контейнеров
docker-compose ps

# 2. Логи backend (самое важное!)
docker-compose logs --tail=100 backend

# 3. Доступность backend
docker-compose exec frontend wget -q -O- http://backend:8000/health
```

### Шаг 4: Наиболее вероятное решение

**Если LDAP включен и недоступен:**

```bash
# 1. Отредактируйте .env файл
nano backend_django/.env
# или
vi backend_django/.env

# 2. Измените:
LDAP_ENABLED=false

# 3. Сохраните и перезапустите backend
docker-compose restart backend

# 4. Проверьте логи
docker-compose logs -f backend
```

**Если backend не запущен:**

```bash
# 1. Проверьте логи
docker-compose logs backend

# 2. Перезапустите все
docker-compose restart

# 3. Если не помогло - пересоберите
docker-compose up -d --build backend
```

**Если проблема с подключением к БД:**

```bash
# 1. Проверьте, что PostgreSQL запущен
docker-compose ps postgres

# 2. Проверьте логи PostgreSQL
docker-compose logs postgres

# 3. Перезапустите PostgreSQL
docker-compose restart postgres
```

### Шаг 5: Проверьте результат

```bash
# Проверьте health endpoint
curl http://localhost:3000/api/health

# Должно вернуть: {"ok": true}
```

## Экспорт логов для анализа на Windows

Если нужно проанализировать логи на Windows:

```bash
# На Ubuntu сервере
docker-compose logs backend > backend_logs.txt
docker-compose logs frontend > frontend_logs.txt
docker-compose logs postgres > postgres_logs.txt

# Скачайте файлы на Windows через SCP
# На Windows (в PowerShell):
scp user@192.168.32.100:/path/to/edu_atg/*_logs.txt ./
```

## Мониторинг в реальном времени

```bash
# Следить за логами backend и frontend
docker-compose logs -f backend frontend

# В другом терминале попробуйте войти
# Смотрите, что появляется в логах
```

## Если ничего не помогло

1. **Полная перезагрузка:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. **Проверьте системные ресурсы:**
   ```bash
   df -h  # Диск
   free -h  # Память
   docker stats --no-stream  # Ресурсы контейнеров
   ```

3. **Проверьте Docker:**
   ```bash
   docker ps
   docker network ls
   ```

4. **Экспортируйте все логи:**
   ```bash
   docker-compose logs > all_logs_$(date +%Y%m%d_%H%M%S).txt 2>&1
   ```

