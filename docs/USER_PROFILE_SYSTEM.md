# 👤 Система профиля пользователя

## 📋 Обзор

Полноценная система управления профилем пользователя с интеграцией Supabase, включающая:
- Управление профилем
- Загрузку фото
- Участие в курсах
- Отслеживание прогресса
- Сертификаты

## 🗄️ Структура базы данных

### Таблицы в Supabase

#### `user_profiles`
Расширенные данные профиля пользователя:
- `id` (UUID) - ID пользователя
- `full_name` - Полное имя
- `email` - Email
- `avatar_url` - URL аватара
- `company` - Компания
- `position` - Должность
- `phone` - Телефон
- `bio` - Описание
- `language` - Язык интерфейса
- `email_notifications` - Email уведомления
- `push_notifications` - Push уведомления
- `weekly_report` - Еженедельный отчет

#### `courses`
Курсы системы:
- `id` - ID курса
- `title` - Название
- `description` - Описание
- `station_id` - ID станции
- `duration_hours` - Длительность (часов)
- `level` - Уровень сложности
- `is_active` - Активен ли
- `icon` - Иконка

#### `user_courses`
Участие пользователей в курсах:
- `id` - ID записи
- `user_id` - ID пользователя
- `course_id` - ID курса
- `progress_percent` - Процент выполнения
- `status` - Статус (in_progress, completed, not_started)
- `started_at` - Дата начала
- `completed_at` - Дата завершения
- `hours_studied` - Часов изучено
- `last_activity` - Последняя активность

#### `certificates`
Сертификаты пользователей:
- `id` - ID сертификата
- `user_id` - ID пользователя
- `course_id` - ID курса
- `title` - Название
- `issued_at` - Дата выдачи
- `pdf_url` - URL PDF

#### `user_stats`
Статистика пользователя:
- `user_id` - ID пользователя
- `active_courses` - Активных курсов
- `completed_courses` - Завершенных курсов
- `total_hours_studied` - Всего часов
- `certificates_count` - Количество сертификатов
- `achievements` - Достижения (JSON)
- `last_updated` - Последнее обновление

## 🔧 API сервиса `userProfile.js`

### Основные методы

#### `getProfile(userId)`
Получить профиль пользователя:
```javascript
const result = await userProfileService.getProfile(userId)
// { success: true, data: { ... } }
```

#### `saveProfile(userId, profileData)`
Сохранить профиль:
```javascript
await userProfileService.saveProfile(userId, {
  full_name: 'Иван Иванов',
  email: 'ivan@example.com',
  bio: 'Описание'
})
```

#### `uploadAvatar(userId, file)`
Загрузить аватар:
```javascript
await userProfileService.uploadAvatar(userId, file)
// Если storage не настроен, сохраняет как base64
```

#### `getUserCourses(userId)`
Получить курсы пользователя:
```javascript
const result = await userProfileService.getUserCourses(userId)
// { success: true, data: [ { course, progress, status } ] }
```

#### `enrollInCourse(userId, courseId)`
Записаться на курс:
```javascript
await userProfileService.enrollInCourse(userId, courseId)
```

#### `updateCourseProgress(userId, courseId, progress)`
Обновить прогресс:
```javascript
await userProfileService.updateCourseProgress(userId, courseId, 75)
```

#### `getUserStats(userId)`
Получить статистику:
```javascript
const result = await userProfileService.getUserStats(userId)
// { active_courses, completed_courses, total_hours_studied, ... }
```

#### `getCertificates(userId)`
Получить сертификаты:
```javascript
const result = await userProfileService.getCertificates(userId)
```

## 📱 Компоненты

### Dashboard.vue
- Отображает статистику пользователя
- Загружает данные из Supabase
- Показывает активные курсы
- Рекомендации курсов
- Достижения

### Profile.vue
- Управление профилем
- Загрузка фото аватара
- Редактирование данных
- Настройки уведомлений
- Просмотр курсов
- Сертификаты

## 🚀 Использование

### Загрузка данных при входе

```javascript
// В компоненте
onMounted(async () => {
  const currentUser = authService.getCurrentUser()
  if (currentUser) {
    // Загружаем профиль
    const profile = await userProfileService.getProfile(currentUser.id)
    
    // Загружаем статистику
    const stats = await userProfileService.getUserStats(currentUser.id)
    
    // Загружаем курсы
    const courses = await userProfileService.getUserCourses(currentUser.id)
  }
})
```

### Загрузка фото

```vue
<el-upload
  action="#"
  :auto-upload="false"
  :on-change="handleAvatarChange"
>
  <el-button>Загрузить фото</el-button>
</el-upload>

<script>
const handleAvatarChange = async (file) => {
  const result = await userProfileService.uploadAvatar(userId, file.raw)
  if (result.success) {
    // Фото загружено
  }
}
</script>
```

### Запись на курс

```javascript
// При переходе на детальную страницу курса
await userProfileService.enrollInCourse(userId, courseId)
```

### Обновление прогресса

```javascript
// После завершения урока
await userProfileService.updateCourseProgress(userId, courseId, 50) // 50%

// После завершения курса
await userProfileService.updateCourseProgress(userId, courseId, 100)
```

## 📸 Загрузка файлов

### Вариант 1: Supabase Storage (рекомендуется)

1. Создайте bucket в Supabase Dashboard
2. Настройте политики доступа
3. Используйте API для загрузки

### Вариант 2: Base64 (по умолчанию)

Если storage не настроен, фото сохраняется как base64 в базе данных.

## 🔐 Безопасность

- Все операции требуют авторизованного пользователя
- RLS политики можно включить когда нужно
- Проверка прав доступа на уровне приложения

## 📊 Миграции

Выполнены миграции:
- ✅ Создание таблицы `user_profiles`
- ✅ Создание таблицы `courses`
- ✅ Создание таблицы `user_courses`
- ✅ Создание таблицы `certificates`
- ✅ Создание таблицы `user_stats`
- ✅ Создание индексов

## 🎯 Следующие шаги

1. Создать тестовые курсы в таблице `courses`
2. Настроить bucket для загрузки файлов
3. Добавить RLS политики
4. Реализовать генерацию PDF сертификатов
5. Добавить уведомления

---
**Дата создания**: 23 января 2025  
**Статус**: ✅ Готово  
**Версия**: 1.0

