# LDAP Testing Guide

## Тестирование LDAP соединения

### 1. Проверка конфигурации (GET)

```bash
GET /api/accounts/ldap/test
```

Возвращает текущую конфигурацию LDAP без чувствительных данных.

**Пример ответа:**
```json
{
  "success": true,
  "message": "LDAP Configuration loaded",
  "config": {
    "server": "ldap://DC03.atg.uz",
    "base_dn": "dc=company,dc=com",
    "user_search_base": "dc=company,dc=com",
    "user_search_filter": "(sAMAccountName={username})",
    "enabled": true
  }
}
```

### 2. Тестирование аутентификации (POST)

```bash
POST /api/accounts/ldap/test
Content-Type: application/json

{
  "username": "a.kuchkarov@atg.uz",
  "password": "your_password"
}
```

**Успешный ответ:**
```json
{
  "success": true,
  "message": "Authentication successful!",
  "user": {
    "username": "a.kuchkarov@atg.uz",
    "email": "a.kuchkarov@atg.uz",
    "full_name": "Full Name",
    "groups": ["Group1", "Group2"]
  }
}
```

**Ошибка аутентификации:**
```json
{
  "success": false,
  "message": "Invalid username or password"
}
```

## Поддерживаемые форматы username

LDAP аутентификатор автоматически пробует несколько форматов:

1. **UPN формат** (если username не содержит @):
   - `username@domain.com`
   - Пример: `a.kuchkarov@atg.uz`

2. **NetBIOS формат** (если username не содержит \):
   - `DOMAIN\username`
   - Пример: `ATG\a.kuchkarov`

3. **Как есть** (если username уже содержит @ или \):
   - Используется точно так, как указано
   - Пример: `a.kuchkarov@atg.uz` → используется как есть

## Примеры использования

### cURL

```bash
# Проверка конфигурации
curl http://localhost:8000/api/accounts/ldap/test

# Тестирование аутентификации
curl -X POST http://localhost:8000/api/accounts/ldap/test \
  -H "Content-Type: application/json" \
  -d '{"username": "a.kuchkarov@atg.uz", "password": "1234567"}'
```

### JavaScript (fetch)

```javascript
// Проверка конфигурации
fetch('/api/accounts/ldap/test')
  .then(res => res.json())
  .then(data => console.log(data));

// Тестирование аутентификации
fetch('/api/accounts/ldap/test', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'a.kuchkarov@atg.uz',
    password: '1234567'
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## Логирование

Все операции LDAP логируются в Django консоль с префиксом `[LDAP]`:

```
[LDAP] Attempting authentication for user: a.kuchkarov@atg.uz
[LDAP] Trying PROVIDED bind: a.kuchkarov@atg.uz
[LDAP] PROVIDED bind successful for: a.kuchkarov@atg.uz
[LDAP] Authentication successful for: a.kuchkarov@atg.uz
```

## Устранение неполадок

1. **"ldap3 package is not installed"**
   - Установите: `pip install ldap3`

2. **"Cannot connect to server"**
   - Проверьте доступность LDAP сервера
   - Проверьте настройки `LDAP_SERVER` в `env.txt`

3. **"Invalid username or password"**
   - Проверьте правильность credentials
   - Попробуйте разные форматы username (с @ и без)

4. **"LDAP is not enabled"**
   - Установите `LDAP_ENABLED=true` в `env.txt`

