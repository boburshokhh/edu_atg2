# Исправление ошибки "value too long for type character varying(255)"

## Проблема

При попытке входа возникает ошибка:
```
Internal server error: value too long for type character varying(255)
```

## Причина

Поле `session_token` в таблице `user_sessions` имеет тип `VARCHAR(255)`, но JWT refresh токены могут быть длиннее 255 символов.

## Решение

### Вариант 1: Использовать Django команду (рекомендуется)

```powershell
cd backend_django
python manage.py fix_session_token
```

Команда автоматически:
1. Проверит текущий тип колонки
2. Изменит `VARCHAR(255)` на `TEXT` если нужно
3. Покажет результат операции

### Вариант 2: Выполнить SQL напрямую

Подключитесь к базе данных и выполните:

```sql
ALTER TABLE user_sessions 
ALTER COLUMN session_token TYPE TEXT;
```

### Вариант 3: Использовать SQL файл

```powershell
# Если используете psql
psql -U postgres -d helpdesk -f backend_django/migrations/fix_session_token_length.sql

# Или через Django
python manage.py dbshell < backend_django/migrations/fix_session_token_length.sql
```

## Проверка

После применения миграции проверьте:

```sql
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'user_sessions'
AND column_name = 'session_token';
```

Должно быть:
- `data_type`: `text`
- `character_maximum_length`: `NULL`

## Что было изменено

1. **Модель Django** (`apps/accounts/models.py`):
   - `session_token = models.CharField(max_length=255)` → `session_token = models.TextField()`

2. **Создана команда Django** (`apps/accounts/management/commands/fix_session_token.py`):
   - Автоматическое исправление типа колонки

3. **Создан SQL файл** (`migrations/fix_session_token_length.sql`):
   - Ручное исправление через SQL

## После исправления

1. Перезапустите Django сервер
2. Попробуйте войти снова
3. Ошибка должна исчезнуть

## Примечание

Если таблица `user_sessions` не существует, создайте её:

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);
```

