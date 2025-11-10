# Система авторизации через Supabase

## Обзор

Система авторизации настроена для работы с Supabase и включает в себя:

- **Таблицы базы данных**: `users` и `user_sessions`
- **Сервис авторизации**: `src/services/auth.js`
- **Компоненты**: обновленные `Login.vue` и `Header.vue`
- **Защита маршрутов**: через Vue Router

## Тестовые пользователи

В системе созданы следующие тестовые пользователи:

| Username | Пароль | Роль | Полное имя |
|----------|--------|------|------------|
| `admin` | `password123` | admin | Администратор системы |
| `instructor1` | `password123` | instructor | Инструктор Иванов |
| `user1` | `password123` | user | Пользователь Петров |
| `student1` | `password123` | user | Студент Сидоров |

## Структура базы данных

### Таблица `users`
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(100),
  email VARCHAR(100),
  role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'instructor')),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Таблица `user_sessions`
```sql
CREATE TABLE user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  session_token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ip_address INET,
  user_agent TEXT
);
```

## API сервиса авторизации

### Методы AuthService

#### `login(username, password)`
Авторизация пользователя
```javascript
const result = await authService.login('admin', 'password123')
if (result.success) {
  console.log('Пользователь авторизован:', result.user)
}
```

#### `logout()`
Выход из системы
```javascript
await authService.logout()
```

#### `checkAuth()`
Проверка авторизации
```javascript
const authResult = await authService.checkAuth()
if (authResult.isAuthenticated) {
  console.log('Пользователь авторизован:', authResult.user)
}
```

#### `getCurrentUser()`
Получение текущего пользователя
```javascript
const user = authService.getCurrentUser()
```

#### `hasRole(role)`
Проверка роли пользователя
```javascript
if (authService.hasRole('admin')) {
  // Пользователь является администратором
}
```

#### `isAdmin()` / `isInstructor()`
Проверка конкретных ролей
```javascript
if (authService.isAdmin()) {
  // Показать админ-панель
}
```

## Защита маршрутов

Маршруты с `meta: { requiresAuth: true }` защищены от неавторизованного доступа:

```javascript
{
  path: '/dashboard',
  name: 'Dashboard',
  component: Dashboard,
  meta: { requiresAuth: true }
}
```

## Использование в компонентах

### Проверка авторизации
```vue
<template>
  <div v-if="isAuthenticated">
    Добро пожаловать, {{ userName }}!
  </div>
  <div v-else>
    <router-link to="/login">Войти</router-link>
  </div>
</template>

<script>
import authService from '@/services/auth'

export default {
  computed: {
    isAuthenticated() {
      return authService.getCurrentUser() !== null
    },
    userName() {
      const user = authService.getCurrentUser()
      return user ? user.full_name : 'Пользователь'
    }
  }
}
</script>
```

### Проверка ролей
```vue
<template>
  <div>
    <button v-if="isAdmin" @click="adminAction">
      Админ-действие
    </button>
    <button v-if="isInstructor" @click="instructorAction">
      Действие инструктора
    </button>
  </div>
</template>

<script>
import authService from '@/services/auth'

export default {
  computed: {
    isAdmin() {
      return authService.isAdmin()
    },
    isInstructor() {
      return authService.isInstructor()
    }
  }
}
</script>
```

## Безопасность

### Row Level Security (RLS)
Включена для обеих таблиц с политиками:
- Пользователи могут видеть только свои данные
- Сессии привязаны к пользователям

### Сессии
- Токены сессий генерируются случайно
- Сессии имеют время истечения (24 часа)
- Отслеживается IP адрес и User Agent
- Автоматическая очистка истекших сессий

### Пароли
⚠️ **Важно**: В текущей реализации используется простое сравнение паролей для демонстрации. В продакшене необходимо использовать bcrypt или аналогичные библиотеки для хеширования.

## Развертывание

### Переменные окружения
Создайте файл `.env`:
```env
VITE_SUPABASE_URL=https://fusartgifhigtysskgfg.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
```

### Обновление сервиса
```javascript
// src/services/auth.js
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY
```

## Мониторинг и логи

### Логи авторизации
Все операции авторизации логируются в консоль браузера для отладки.

### Проверка сессий
```sql
-- Активные сессии
SELECT u.username, us.created_at, us.last_activity, us.ip_address
FROM user_sessions us
JOIN users u ON us.user_id = u.id
WHERE us.expires_at > NOW()
ORDER BY us.last_activity DESC;
```

### Очистка истекших сессий
```sql
-- Ручная очистка
SELECT cleanup_expired_sessions();
```

## Расширение функциональности

### Добавление новых ролей
1. Обновите CHECK constraint в таблице users
2. Добавьте методы в AuthService
3. Обновите компоненты для проверки новых ролей

### Интеграция с внешними системами
- OAuth провайдеры (Google, Microsoft)
- LDAP/Active Directory
- Двухфакторная аутентификация

### Уведомления
- Email уведомления о входе
- Push уведомления
- SMS для критических операций

---

**Примечание**: Данная система предназначена для внутреннего использования и демонстрации. Для продакшена рекомендуется дополнительная настройка безопасности и мониторинга.
