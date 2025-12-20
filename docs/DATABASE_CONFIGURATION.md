# Конфигурация базы данных

## Что такое DATABASE_URL?

`DATABASE_URL` — это строка подключения к базе данных PostgreSQL в формате URL. Она содержит всю информацию, необходимую для подключения к базе данных:
- Тип базы данных (postgresql)
- Имя пользователя
- Пароль
- Адрес сервера (host)
- Порт
- Имя базы данных

## Зачем она нужна?

Django приложению нужна база данных для хранения:
- **Пользователей** (логины, пароли, профили)
- **Станций** (обучающие станции)
- **Курсов** (обучающие курсы)
- **Файлов** (метаданные о файлах)
- **Сессий** (токены авторизации)

**Без базы данных приложение не сможет работать!**

## Формат DATABASE_URL

```
postgresql://username:password@host:port/database_name
```

### Примеры:

**Локальная база данных:**
```
postgresql://postgres:postgre@localhost:5432/helpdesk
```

**Удаленная база данных:**
```
postgresql://user:password@192.168.32.100:5432/atg
```

**С указанием порта:**
```
postgresql://postgres:mypassword@localhost:5432/mydb
```

## Как настроить?

### Вариант 1: Использовать DATABASE_URL (рекомендуется)

Добавьте в файл `backend_django/env.txt`:

```env
DATABASE_URL=postgresql://postgres:postgre@localhost:5432/helpdesk
```

### Вариант 2: Использовать отдельные настройки

Если `DATABASE_URL` не указан, используются отдельные переменные:

```env
POSTGRES_DB=atg
POSTGRES_USER=atg
POSTGRES_PASSWORD=atg
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Что делать, если база данных не установлена?

### 1. Установить PostgreSQL

**Windows:**
- Скачайте с https://www.postgresql.org/download/windows/
- Или используйте Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgre postgres`

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
```

### 2. Создать базу данных

```bash
# Войти в PostgreSQL
psql -U postgres

# Создать базу данных
CREATE DATABASE helpdesk;

# Создать пользователя (если нужно)
CREATE USER atg WITH PASSWORD 'atg';
GRANT ALL PRIVILEGES ON DATABASE helpdesk TO atg;
```

### 3. Настроить миграции Django

```bash
cd backend_django
python manage.py migrate
```

## Проверка подключения

### Проверить, что база данных доступна:

```bash
# Проверить подключение через psql
psql -h localhost -U postgres -d helpdesk

# Или проверить через Django
python manage.py dbshell
```

### Проверить настройки Django:

```bash
python manage.py check --database default
```

## Текущая конфигурация

В вашем проекте используется **гибкая конфигурация**:

1. **Если `DATABASE_URL` установлен** → используется он
2. **Если `DATABASE_URL` не установлен** → используются отдельные настройки (`POSTGRES_*`)

Это означает, что `DATABASE_URL` **опциональна** - если её нет, Django использует отдельные настройки.

## Пример env.txt

```env
# База данных (выберите один вариант)

# Вариант 1: DATABASE_URL (всё в одной строке)
DATABASE_URL=postgresql://postgres:postgre@localhost:5432/helpdesk

# ИЛИ Вариант 2: Отдельные настройки
# POSTGRES_DB=helpdesk
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgre
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432

# Другие настройки
DJANGO_SECRET_KEY=your_super_secret_key
LDAP_ENABLED=true
LDAP_SERVER=ldap://DC03.atg.uz
# ...
```

## Устранение проблем

### Ошибка: "connection failed"

**Причина:** База данных не запущена или недоступна

**Решение:**
1. Проверьте, что PostgreSQL запущен
2. Проверьте правильность хоста и порта
3. Проверьте firewall

### Ошибка: "database does not exist"

**Причина:** База данных не создана

**Решение:**
```sql
CREATE DATABASE helpdesk;
```

### Ошибка: "password authentication failed"

**Причина:** Неверный пароль

**Решение:** Проверьте пароль в `DATABASE_URL` или `POSTGRES_PASSWORD`

