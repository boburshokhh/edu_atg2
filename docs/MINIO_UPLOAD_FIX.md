# Быстрое исправление ошибки InvalidAccessKeyId при загрузке

## Проблема
При загрузке файлов появляется ошибка:
```
Upload failed: InvalidAccessKeyId - The Access Key Id you provided does not exist in our records.
```

## Причина
Учетные данные MinIO в файле `backend_django/.env` не совпадают с реальными учетными данными вашего MinIO сервера.

## Решение (3 шага)

### Шаг 1: Найдите реальные учетные данные MinIO

1. Откройте MinIO Admin Console: `http://192.168.32.100:9001`
2. Войдите в систему (логин/пароль)
3. Перейдите в Settings → Access Keys или проверьте конфигурацию сервера

### Шаг 2: Обновите учетные данные

**Вариант А: Вручную (рекомендуется)**

Откройте файл `backend_django/.env` и обновите:

```env
MINIO_ACCESS_KEY=ваш-реальный-access-key
MINIO_SECRET_KEY=ваш-реальный-secret-key
```

**Вариант Б: Через скрипт**

```bash
cd backend_django
python update_minio_credentials.py ваш-access-key ваш-secret-key
```

### Шаг 3: Перезапустите Django сервер

**ОБЯЗАТЕЛЬНО!** После изменения `.env` перезапустите сервер:

```bash
# Остановите сервер (Ctrl+C)
# Затем запустите снова
python manage.py runserver
```

## Проверка

После перезапуска проверьте подключение:

```bash
cd backend_django
python test_minio_connection.py
```

Если все тесты пройдены, загрузка файлов должна работать.

## Дополнительная информация

- Полная документация: `docs/MINIO_CREDENTIALS_SETUP.md`
- Скрипт проверки: `backend_django/test_minio_connection.py`
- Скрипт обновления: `backend_django/update_minio_credentials.py`

