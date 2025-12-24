# Исправление структуры проекта на сервере

## Проблема
```
failed to solve: "/backend_django": not found
```

## Причина
На сервере отсутствует папка `backend_django` или структура проекта отличается.

## Решение

### Вариант 1: Проверьте структуру на сервере

```bash
cd ~/edu_atg
ls -la

# Проверьте, как называется папка с backend
ls -d */ | grep -E "(backend|django|api)"
```

### Вариант 2: Если папка называется по-другому

Если на сервере папка называется `backend` вместо `backend_django`:

```bash
# Переименуйте или создайте симлинк
cd ~/edu_atg
mv backend backend_django
# или
ln -s backend backend_django
```

### Вариант 3: Если структура полностью другая

Если backend находится в другом месте, обновите `docker-compose.yml`:

```yaml
backend:
  build:
    context: ./ваша_папка_с_backend
    dockerfile: docker/Dockerfile
```

### Вариант 4: Создайте правильную структуру

Если папки `backend_django` нет вообще:

```bash
cd ~/edu_atg

# 1. Проверьте, что есть
ls -la

# 2. Если есть git репозиторий, получите код
git pull

# 3. Если нет git, скопируйте папку backend_django с вашего компьютера
# На вашем компьютере:
# scp -r backend_django root@edusite:~/edu_atg/

# 4. Проверьте структуру
ls -la backend_django/
ls -la backend_django/docker/Dockerfile
ls -la migrations/
```

### Вариант 5: Используйте обновленный docker-compose.yml

Я обновил `docker-compose.yml` чтобы использовать build context `./backend_django`. 

**На сервере выполните:**

```bash
cd ~/edu_atg

# 1. Обновите docker-compose.yml (скопируйте с вашего компьютера или через git pull)
# 2. Убедитесь, что структура правильная:
ls -la backend_django/
ls -la backend_django/docker/Dockerfile
ls -la migrations/

# 3. Если все на месте, соберите:
docker compose build --no-cache backend
docker compose up -d
```

## Правильная структура на сервере

```
~/edu_atg/
├── backend_django/          # ← Должна существовать!
│   ├── docker/
│   │   └── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   └── ...
├── migrations/              # ← Должна существовать!
│   ├── complete_database_schema.sql
│   └── ...
├── docker-compose.yml
├── Dockerfile.frontend
├── nginx.conf
└── .env
```

## Быстрая диагностика

```bash
cd ~/edu_atg

echo "=== Проверка структуры ==="
[ -d backend_django ] && echo "✓ backend_django/ существует" || echo "✗ backend_django/ НЕ существует"
[ -d backend_django/docker ] && echo "✓ backend_django/docker/ существует" || echo "✗ backend_django/docker/ НЕ существует"
[ -f backend_django/docker/Dockerfile ] && echo "✓ Dockerfile существует" || echo "✗ Dockerfile НЕ существует"
[ -f backend_django/requirements.txt ] && echo "✓ requirements.txt существует" || echo "✗ requirements.txt НЕ существует"
[ -d migrations ] && echo "✓ migrations/ существует" || echo "✗ migrations/ НЕ существует"

echo ""
echo "=== Содержимое корня ==="
ls -la | head -20

echo ""
echo "=== Поиск backend папок ==="
find . -maxdepth 2 -type d -name "*backend*" -o -name "*django*" 2>/dev/null
```

## После исправления структуры

```bash
cd ~/edu_atg
docker compose build --no-cache backend
docker compose up -d
docker compose ps
docker compose logs -f backend
```

