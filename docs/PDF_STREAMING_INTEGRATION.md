# Интеграция PDF Streaming из MinIO

## Обзор

Система безопасного отображения PDF документов из MinIO через backend streaming endpoint с использованием PDF.js на frontend.

## Архитектура

### Backend (Django)
- **Endpoint**: `/api/files/stream/{objectKey}`
- **Метод**: `GET` (с поддержкой `OPTIONS` для CORS)
- **Аутентификация**: `IsAuthenticated` (JWT токен)
- **Поддержка**: Range requests для частичной загрузки

### Frontend (Vue.js)
- **Компонент**: `SecurePDFViewer.vue`
- **Библиотека**: `pdfjs-dist`
- **Метод загрузки**: Streaming через `/api/files/stream/`

## Поток данных

```
1. Frontend: SecurePDFViewer получает objectKey из props.file
2. Frontend: Кодирует ключ через encodeURIComponent()
3. Frontend: Формирует URL: /api/files/stream/{encodedKey}
4. Frontend: Передает JWT токен в заголовке Authorization
5. Backend: StreamObjectView декодирует ключ
6. Backend: Проверяет аутентификацию (IsAuthenticated)
7. Backend: Загружает файл из MinIO через boto3
8. Backend: Определяет Content-Type (application/pdf)
9. Backend: Возвращает StreamingHttpResponse с Range support
10. Frontend: PDF.js загружает PDF по частям (Range requests)
11. Frontend: Рендерит PDF на Canvas
```

## Ключевые особенности безопасности

### Backend
- ✅ Требуется JWT аутентификация
- ✅ Нет прямого доступа к MinIO из браузера
- ✅ Все запросы логируются
- ✅ Правильное определение Content-Type
- ✅ Поддержка Range requests для эффективной загрузки

### Frontend
- ✅ Загрузка через streaming endpoint (не presigned URLs)
- ✅ JWT токен передается в заголовках
- ✅ Защита от скачивания (блокировка контекстного меню)
- ✅ Защита от печати (CSS @media print)
- ✅ Отключение выделения текста на Canvas

## Настройка

### Backend

1. **URL маршрут** (уже настроен):
```python
# backend_django/apps/files/urls.py
re_path(r"^stream/(?P<key>.+)$", views.StreamObjectView.as_view()),
```

2. **CORS** (уже настроен в settings.py):
```python
CORS_ALLOW_ALL_ORIGINS = True  # или список разрешенных origins
```

3. **MinIO настройки** (проверьте .env):
```env
MINIO_ENDPOINT=http://192.168.32.100:9000
MINIO_BUCKET=atgedu
MINIO_ACCESS_KEY=your_key
MINIO_SECRET_KEY=your_secret
```

### Frontend

1. **Установка зависимостей** (уже установлено):
```bash
npm install pdfjs-dist
```

2. **Использование компонента**:
```vue
<SecurePDFViewer
  :file="currentFile"
  :zoom="currentZoom"
  :is-fullscreen="isFullscreen"
  @zoom-in="$emit('zoom-in')"
  @zoom-out="$emit('zoom-out')"
/>
```

## Отладка

### Backend логи
```python
# Включите DEBUG логирование в Django settings
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.files.views': {
            'level': 'DEBUG',
        },
    },
}
```

### Frontend логи
Откройте DevTools Console - все операции логируются:
- `[SecurePDFViewer] Loading PDF:` - начало загрузки
- `[SecurePDFViewer] PDF loaded successfully:` - успешная загрузка
- `[SecurePDFViewer] Error loading PDF:` - ошибки

### Типичные проблемы

1. **401 Unauthorized**
   - Проверьте наличие JWT токена в localStorage
   - Проверьте, что токен не истек
   - Проверьте заголовок Authorization в Network tab

2. **404 Not Found**
   - Проверьте objectKey в props.file
   - Проверьте, что файл существует в MinIO
   - Проверьте правильность bucket name

3. **CORS ошибки**
   - Проверьте настройки CORS в Django settings
   - Проверьте, что Origin заголовок правильный
   - Проверьте OPTIONS запрос в Network tab

4. **PDF не отображается**
   - Проверьте Content-Type в ответе (должен быть application/pdf)
   - Проверьте Range requests в Network tab
   - Проверьте ошибки в Console

## Тестирование

### Ручное тестирование

1. Откройте DevTools → Network
2. Перейдите на страницу с PDF
3. Проверьте запросы:
   - `GET /api/files/stream/{key}` - должен вернуть 200 или 206
   - Заголовки должны содержать `Content-Type: application/pdf`
   - Для Range requests должен быть `Content-Range`

### Проверка Range requests

PDF.js использует Range requests для частичной загрузки:
```
Range: bytes=0-1023
→ 206 Partial Content
Content-Range: bytes 0-1023/1234567
```

## Производительность

- **Streaming**: Файл загружается по частям, не весь сразу
- **Range requests**: PDF.js запрашивает только нужные части
- **Кэширование**: PDF не кэшируется (безопасность), другие файлы кэшируются 1 час

## Безопасность

### Защита PDF
- ❌ Нет presigned URLs для PDF
- ✅ Только streaming через authenticated endpoint
- ✅ JWT токен обязателен
- ✅ Логирование всех запросов
- ✅ Защита от скачивания на frontend

### Ограничения
- ⚠️ 100% защита невозможна (можно сделать скриншот)
- ⚠️ Опытный пользователь может извлечь данные
- ✅ Защита основана на усложнении доступа

## Дальнейшие улучшения

1. **Rate limiting** на backend для `/api/files/stream/`
2. **Watermarking** PDF на лету
3. **Аудит логи** для всех запросов к PDF
4. **Проверка прав доступа** к конкретным документам
5. **CDN кэширование** для публичных файлов (не PDF)

