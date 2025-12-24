# Исправление ошибки ContainerConfig

Если вы получили ошибку `KeyError: 'ContainerConfig'`, выполните следующие команды:

```bash
# 1. Остановите и удалите все контейнеры
docker-compose down

# 2. Удалите старый образ backend
docker rmi edu_atg_backend 2>/dev/null || true
docker rmi $(docker images | grep backend | awk '{print $3}') 2>/dev/null || true

# 3. Очистите кеш сборки (опционально)
docker builder prune -f

# 4. Пересоберите backend с нуля
docker-compose build --no-cache backend

# 5. Запустите снова
docker-compose up -d backend

# 6. Проверьте логи
docker-compose logs -f backend
```

Если проблема сохраняется, попробуйте:

```bash
# Полная очистка
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

