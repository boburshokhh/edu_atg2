# Тестовые пользователи для системы авторизации

## Список всех тестовых пользователей

Все пользователи используют пароль: **`password123`**

### Администраторы
| Username | Полное имя | Email | Роль |
|----------|------------|-------|------|
| `admin` | Администратор системы | admin@atg.uz | admin |

### Инструкторы
| Username | Полное имя | Email | Роль |
|----------|------------|-------|------|
| `instructor1` | Инструктор Иванов | instructor1@atg.uz | instructor |
| `supervisor1` | Супервайзер Волков | supervisor1@atg.uz | instructor |

### Пользователи
| Username | Полное имя | Email | Роль |
|----------|------------|-------|------|
| `user1` | Пользователь Петров | user1@atg.uz | user |
| `student1` | Студент Сидоров | student1@atg.uz | user |
| `engineer1` | Инженер Козлов | engineer1@atg.uz | user |
| `operator1` | Оператор Смирнов | operator1@atg.uz | user |
| `technician1` | Техник Морозов | technician1@atg.uz | user |

## Быстрый тест авторизации

### Для тестирования администратора:
- **Логин:** `admin`
- **Пароль:** `password123`
- **Роль:** Администратор (полный доступ)

### Для тестирования инструктора:
- **Логин:** `instructor1` или `supervisor1`
- **Пароль:** `password123`
- **Роль:** Инструктор (доступ к обучению и управлению)

### Для тестирования обычного пользователя:
- **Логин:** `student1`, `engineer1`, `operator1`, `technician1` или `user1`
- **Пароль:** `password123`
- **Роль:** Пользователь (базовый доступ)

## Проверка в базе данных

Для проверки всех пользователей в Supabase выполните SQL запрос:

```sql
SELECT username, full_name, role, is_active, created_at 
FROM users 
ORDER BY role, username;
```

## Сброс паролей

Если нужно изменить пароль для всех пользователей, выполните:

```sql
-- Обновление пароля для всех пользователей
UPDATE users 
SET password_hash = '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
    updated_at = NOW()
WHERE is_active = true;
```

## Добавление новых пользователей

Для добавления нового пользователя:

```sql
INSERT INTO users (username, password_hash, full_name, email, role) VALUES
('newuser', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Новый Пользователь', 'newuser@atg.uz', 'user');
```

## Деактивация пользователей

Для деактивации пользователя:

```sql
UPDATE users 
SET is_active = false, updated_at = NOW() 
WHERE username = 'username_to_deactivate';
```

---

**Примечание:** В текущей реализации используется простое сравнение паролей для демонстрации. В продакшене необходимо использовать bcrypt для хеширования паролей.
