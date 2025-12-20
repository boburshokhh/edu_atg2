# Настройка учетных данных MinIO

## Проблема

Если вы видите ошибку `InvalidAccessKeyId` при попытке доступа к файлам в MinIO, это означает, что учетные данные MinIO в Django не совпадают с реальными учетными данными вашего MinIO сервера.

## Решение

### Шаг 1: Узнайте реальные учетные данные MinIO

Учетные данные MinIO можно найти:

1. **В конфигурации MinIO сервера** (если вы его настраивали)
2. **В MinIO Admin Console** (обычно `http://192.168.32.100:9001`)
3. **В переменных окружения** вашего MinIO сервера
4. **В docker-compose.yml** (если MinIO запущен в Docker)

### Шаг 2: Создайте файл `.env` в `backend_django/`

Скопируйте пример файла:

```bash
cd backend_django
cp .env.example .env
```

Или создайте файл `backend_django/.env` вручную со следующим содержимым:

```env
# MinIO Configuration
MINIO_ENDPOINT=http://192.168.32.100:9000
MINIO_BUCKET=atgedu
MINIO_ACCESS_KEY=ваш-реальный-access-key
MINIO_SECRET_KEY=ваш-реальный-secret-key
```

**Важно:** Замените `ваш-реальный-access-key` и `ваш-реальный-secret-key` на реальные учетные данные из вашего MinIO сервера.

### Шаг 3: Проверьте подключение

Запустите скрипт проверки:

```bash
cd backend_django
python test_minio_connection.py
```

Скрипт проверит:
- ✓ Подключение к MinIO серверу
- ✓ Существование bucket `atgedu`
- ✓ Возможность чтения объектов
- ✓ Генерацию presigned URL

### Шаг 4: Перезапустите Django сервер

После изменения `.env` файла необходимо перезапустить Django:

```bash
# Остановите сервер (Ctrl+C)
# Затем запустите снова
python manage.py runserver
```

## Альтернативное решение: Использование Stream Endpoint

Если вы не можете изменить учетные данные MinIO, админ-панель уже настроена на использование stream endpoint (`/api/files/stream/<key>`), который работает через Django и использует правильные учетные данные. Это должно работать даже если presigned URL не работают.

## Проверка текущих настроек

Текущие настройки MinIO в Django можно посмотреть в:
- `backend_django/atg_backend/settings.py` (строки 140-143)
- Или запустив скрипт проверки подключения

## Частые проблемы

### Проблема: "InvalidAccessKeyId"
**Решение:** Убедитесь, что `MINIO_ACCESS_KEY` в `.env` совпадает с Access Key в MinIO сервере.

### Проблема: "SignatureDoesNotMatch"
**Решение:** Убедитесь, что `MINIO_SECRET_KEY` в `.env` совпадает с Secret Key в MinIO сервере.

### Проблема: "Bucket does not exist"
**Решение:** Создайте bucket `atgedu` в MinIO Admin Console или измените `MINIO_BUCKET` в `.env` на существующий bucket.

