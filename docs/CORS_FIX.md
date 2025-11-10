# Исправление CORS ошибок для MinIO

## 🔴 Проблема

При работе с MinIO возникают CORS ошибки:
```
Access to fetch at 'https://minio.dmed.gubkin.uz/api/atgedu/...' 
from origin 'http://localhost:3000' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## ✅ Решение

### 1. Настройка CORS в MinIO

Необходимо настроить CORS в MinIO для разрешения запросов с вашего домена.

#### Через MinIO Console:

1. Откройте MinIO Console: `http://dmed.gubkin.uz:9001`
2. Войдите с credentials: `admin` / `1234bobur$`
3. Перейдите в **Settings** → **CORS**
4. Добавьте следующие правила:

```json
[
  {
    "AllowedOrigins": [
      "http://localhost:3000",
      "http://localhost:5173",
      "https://your-production-domain.com"
    ],
    "AllowedMethods": [
      "GET",
      "PUT",
      "POST",
      "DELETE",
      "HEAD"
    ],
    "AllowedHeaders": [
      "*"
    ],
    "ExposeHeaders": [
      "ETag",
      "Content-Length",
      "Content-Type"
    ],
    "MaxAgeSeconds": 3000
  }
]
```

#### Через MinIO CLI (mc):

```bash
# Установите mc (MinIO Client)
# Затем выполните:

mc alias set myminio http://dmed.gubkin.uz:9000 admin 1234bobur$

# Создайте файл cors.json:
cat > cors.json << EOF
[
  {
    "AllowedOrigins": ["http://localhost:3000", "http://localhost:5173", "https://your-domain.com"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag", "Content-Length", "Content-Type"],
    "MaxAgeSeconds": 3000
  }
]
EOF

# Примените CORS правила:
mc anonymous set-json cors.json myminio/atgedu
```

### 2. Проверка конфигурации

Убедитесь, что в проекте используется правильный endpoint:

```javascript
// src/services/minioService.js
const MINIO_ENDPOINT = 'http://dmed.gubkin.uz:9000' // Без /api, без HTTPS
```

### 3. Перезапуск dev сервера

После изменения конфигурации:

```bash
# Остановите dev сервер (Ctrl+C)
# Очистите кеш браузера (Ctrl+Shift+R)
# Запустите заново:
npm run dev
```

## 🔍 Проверка

### 1. Проверка CORS настроек

В консоли браузера выполните:

```javascript
fetch('http://dmed.gubkin.uz:9000/atgedu/', {
  method: 'HEAD',
  mode: 'cors'
})
.then(r => console.log('CORS работает!', r))
.catch(e => console.error('CORS ошибка:', e))
```

### 2. Проверка endpoint

Убедитесь, что endpoint правильный:

```javascript
console.log(import.meta.env.VITE_MINIO_ENDPOINT)
// Должно быть: http://dmed.gubkin.uz:9000
```

## 📝 Важные моменты

1. **Endpoint должен быть HTTP**: `http://dmed.gubkin.uz:9000` (не HTTPS, не `/api`)
2. **CORS должен быть настроен** в MinIO для вашего домена
3. **Перезапустите dev сервер** после изменения `.env` файла
4. **Очистите кеш браузера** если проблемы продолжаются

## 🐛 Troubleshooting

### Проблема: Все еще появляется `/api/` в URL

**Решение**:
1. Проверьте `.env` файл - не должно быть `/api` в endpoint
2. Перезапустите dev сервер
3. Очистите кеш браузера (Ctrl+Shift+R)

### Проблема: CORS ошибки продолжаются

**Решение**:
1. Проверьте CORS настройки в MinIO Console
2. Убедитесь, что ваш домен добавлен в `AllowedOrigins`
3. Проверьте, что bucket `atgedu` существует

### Проблема: URL содержит `minio.dmed.gubkin.uz` вместо `dmed.gubkin.uz:9000`

**Решение**:
1. Проверьте переменные окружения: `console.log(import.meta.env.VITE_MINIO_ENDPOINT)`
2. Убедитесь, что в `.env` файле правильный endpoint
3. Перезапустите dev сервер

