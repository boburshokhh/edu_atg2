# Исправление ошибки сборки Frontend

## Проблема
```
npm error The `npm ci` command can only install with an existing package-lock.json
```

## Причина
Файл `package-lock.json` был исключен из build context через `.dockerignore`, но он необходим для команды `npm ci`.

## Решение

### На сервере обновите `.dockerignore`:

```bash
cd ~/edu_atg
nano .dockerignore
```

Измените строку:
```
package-lock.json
```

На:
```
# package-lock.json - НЕ исключаем, нужен для npm ci в frontend build
```

Или удалите эту строку полностью.

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Затем пересоберите frontend:

```bash
docker compose build --no-cache frontend
docker compose up -d
```

## Альтернативное решение (если нет package-lock.json)

Если на сервере нет `package-lock.json`, можно изменить Dockerfile.frontend:

```dockerfile
# Вместо npm ci используйте npm install
RUN npm install
```

Но лучше использовать `npm ci` для воспроизводимых сборок.

## Проверка

```bash
# 1. Убедитесь, что package-lock.json существует
ls -la package-lock.json

# 2. Проверьте .dockerignore
grep -n "package-lock" .dockerignore

# 3. Соберите frontend
docker compose build --no-cache frontend

# 4. Запустите
docker compose up -d frontend

# 5. Проверьте логи
docker compose logs -f frontend
```

