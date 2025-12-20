# Упрощенная конфигурация Vite

## Что было сделано

### ✅ Упрощения

1. **Убраны сложные плагины:**
   - Compression плагины (gzip, brotli)
   - Bundle visualizer
   - Лишние функции

2. **Упрощен proxy:**
   - Только два простых proxy:
     - `/api/minio` → MinIO сервер (для файлов)
     - `/api` → Django бэкенд (localhost:8000)

3. **Убраны дублирования:**
   - Один `resolve.alias` вместо двух
   - Упрощенная загрузка env переменных

4. **Убраны упоминания Supabase:**
   - Все настройки только для Django бэкенда

## Структура proxy

### Django API Proxy

```
Frontend запрос: /api/auth/login
         ↓
Vite Proxy: убирает /api
         ↓
Django: http://localhost:8000/auth/login
```

**Все роуты Django:**
- `/api/auth/*` → `http://localhost:8000/auth/*`
- `/api/users/*` → `http://localhost:8000/users/*`
- `/api/stations/*` → `http://localhost:8000/stations/*`
- `/api/courses/*` → `http://localhost:8000/courses/*`
- `/api/files/*` → `http://localhost:8000/files/*`
- `/api/health` → `http://localhost:8000/health`

### MinIO Proxy

```
Frontend запрос: /api/minio/bucket/file.jpg
         ↓
Vite Proxy: убирает /api/minio
         ↓
MinIO: http://192.168.32.100:9000/bucket/file.jpg
```

## Настройки

Все настройки берутся из `frontend.env`:

```env
VITE_API_TARGET=http://localhost:8000
VITE_MINIO_TARGET=http://192.168.32.100:9000
VITE_MINIO_ENDPOINT=http://192.168.32.100:9000
VITE_MINIO_BUCKET=atgedu
VITE_MINIO_ACCESS_KEY=minioadmin
VITE_MINIO_SECRET_KEY=minioadmin
VITE_LDAP_ENABLED=true
```

## Использование в коде

### Frontend запросы

Все запросы к Django идут через `/api`:

```javascript
// Авторизация
fetch('/api/auth/login', { ... })

// Получение станций
fetch('/api/stations/', { ... })

// Получение курсов
fetch('/api/courses/', { ... })

// Файлы
fetch('/api/files/presign?key=...', { ... })
```

Vite автоматически проксирует на `http://localhost:8000`.

## Преимущества

1. **Простота** - один путь для всего бэкенда
2. **Понятность** - легко понять, куда идут запросы
3. **Без Supabase** - только наш Django бэкенд
4. **Легко поддерживать** - минимум настроек

## Проверка

После изменений:

1. **Перезапустите Vite:**
   ```powershell
   npm run dev
   ```

2. **Проверьте, что proxy работает:**
   - Откройте DevTools → Network
   - Сделайте запрос (например, логин)
   - Проверьте, что запрос идет на `/api/*`
   - Проверьте, что Status = 200 OK

3. **Проверьте Django логи:**
   - Должны видеть запросы на `http://localhost:8000/*`

