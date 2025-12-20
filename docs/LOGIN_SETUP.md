# Настройка логина через Django API

## Как работает логин

### 1. Frontend (Login.vue)

При нажатии кнопки "Войти":
1. Валидация формы (username и password обязательны)
2. Вызов `authService.login(username, password)`
3. Обработка результата и перенаправление

### 2. AuthService (auth.js)

`authService.login()` делает:
1. POST запрос на `/api/auth/login` (проксируется на Django)
2. Отправляет `{username, password}` в JSON
3. Получает ответ с токенами и информацией о пользователе
4. Сохраняет токены в localStorage
5. Возвращает `{success: true, user: {...}}` или `{success: false, error: "..."}`

### 3. Vite Proxy (vite.config.js)

В режиме разработки:
- Запрос `/api/auth/login` → проксируется на `http://localhost:8000/auth/login`
- Это позволяет избежать проблем с CORS

### 4. Django Backend (views.py)

`LoginView.post()`:
1. Получает `username` и `password` из запроса
2. Пытается аутентифицировать через LDAP (если включен)
3. Если LDAP не работает, пробует базу данных
4. Генерирует JWT токены (access и refresh)
5. Возвращает JSON:
   ```json
   {
     "token": "access_token",
     "refreshToken": "refresh_token",
     "user": {
       "id": "user_id",
       "username": "username",
       "role": "user|instructor|admin",
       "full_name": "Full Name",
       "email": "email@example.com"
     },
     "expiresIn": 900
   }
   ```

## URL маршруты

- **Frontend запрос**: `/api/auth/login`
- **Vite proxy**: `/api` → `http://localhost:8000`
- **Django URL**: `auth/login` (из `atg_backend/urls.py`)

Итого: `/api/auth/login` → `http://localhost:8000/auth/login`

## Проверка работы

### 1. Проверить, что Django сервер запущен:

```powershell
cd backend_django
python manage.py runserver 8000
```

### 2. Проверить, что Vite dev server запущен:

```powershell
npm run dev
```

### 3. Открыть консоль браузера (F12) и проверить логи:

При попытке входа вы должны увидеть:
```
[Auth] Sending login request to: /api/auth/login
[Auth] API_BASE_URL: /api
[Auth] Response status: 200 OK
```

### 4. Проверить Network tab:

- Запрос должен идти на `/api/auth/login`
- Метод: POST
- Headers: `Content-Type: application/json`
- Body: `{"username": "...", "password": "..."}`
- Response: JSON с токенами и информацией о пользователе

## Устранение проблем

### Ошибка: "Failed to fetch" или "Network error"

**Причина:** Django сервер не запущен или недоступен

**Решение:**
1. Убедитесь, что Django сервер запущен на порту 8000
2. Проверьте, что proxy настроен правильно в `vite.config.js`
3. Проверьте консоль браузера на наличие CORS ошибок

### Ошибка: 404 Not Found

**Причина:** Неправильный URL

**Решение:**
1. Проверьте, что в `vite.config.js` proxy настроен на `/api`
2. Проверьте, что Django URL правильный: `auth/login`
3. Проверьте, что `API_BASE_URL` в `auth.js` правильный

### Ошибка: 401 Unauthorized

**Причина:** Неверные учетные данные

**Решение:**
1. Проверьте username и password
2. Если используется LDAP, проверьте настройки LDAP в `env.txt`
3. Проверьте логи Django для подробной информации

### Ошибка: 500 Internal Server Error

**Причина:** Ошибка на сервере

**Решение:**
1. Проверьте логи Django в консоли
2. Проверьте, что база данных доступна
3. Проверьте настройки LDAP (если используется)

## Логирование

Все операции логируются:

**Frontend (консоль браузера):**
- `[Auth] Sending login request to: ...`
- `[Auth] Response status: ...`
- `[Auth] LDAP authentication successful/failed`

**Backend (консоль Django):**
- `[Auth] Attempting LDAP authentication for user: ...`
- `[Auth] Login successful for user: ...`
- `[LDAP] Attempting authentication for user: ...`

## Тестирование

### Тест через curl:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

### Тест через браузер (консоль):

```javascript
fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'testuser', password: 'testpass' })
})
  .then(res => res.json())
  .then(data => console.log(data))
```

