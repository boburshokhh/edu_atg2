# Исправление ошибки ContainerConfig для frontend

Выполните следующие команды на сервере:

```bash
# 1. Остановите и удалите все контейнеры
docker-compose down

# 2. Удалите старый контейнер frontend (если существует)
docker rm -f edu_frontend 2>/dev/null || true

# 3. Удалите старый образ frontend
docker rmi $(docker images | grep -E "edu_atg.*frontend|frontend.*edu_atg" | awk '{print $3}') 2>/dev/null || true
docker rmi $(docker images | grep "edu_atg_frontend" | awk '{print $3}') 2>/dev/null || true

# 4. Пересоберите frontend с нуля (без кеша)
docker-compose build --no-cache frontend

# 5. Запустите снова
docker-compose up -d frontend

# 6. Проверьте логи
docker-compose logs -f frontend
```

Если проблема сохраняется, выполните полную очистку:

```bash
# Полная очистка
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

