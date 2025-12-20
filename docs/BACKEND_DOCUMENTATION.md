# 📚 Полная документация бэкенда

## 🏗️ Архитектура системы

Платформа обучения ATG Education использует **serverless архитектуру** на основе:

- **Supabase** (PostgreSQL + Storage) - основная база данных и хранилище файлов
- **MinIO** - дополнительное хранилище для больших файлов (PDF, видео)
- **Vue.js 3** - фронтенд фреймворк
- **Vite** - сборщик и dev-сервер

---

## 🔌 Backend сервисы

Все сервисы находятся в директории `src/services/`:

### 1. AuthService (`src/services/auth.js`)

**Назначение**: Управление аутентификацией и авторизацией пользователей

**Зависимости**: 
- `@supabase/supabase-js`

**Основные методы**:

#### `login(username, password)`
Авторизация пользователя в системе.

**Параметры**:
- `username` (string) - имя пользователя
- `password` (string) - пароль

**Возвращает**:
```javascript
{
  success: boolean,
  user?: {
    id: UUID,
    username: string,
    full_name: string,
    email: string,
    role: 'admin' | 'user' | 'instructor',
    is_active: boolean
  },
  token?: string,
  error?: string
}
```

**Логика работы**:
1. Поиск пользователя в таблице `users` по username
2. Проверка пароля (в текущей версии - простое сравнение)
3. Создание сессии в таблице `user_sessions`
4. Сохранение токена в localStorage
5. Возврат данных пользователя

#### `logout()`
Выход из системы.

**Логика**:
1. Удаление сессии из БД
2. Очистка localStorage
3. Сброс текущего пользователя

#### `checkAuth()`
Проверка валидности текущей сессии.

**Возвращает**:
```javascript
{
  isAuthenticated: boolean,
  user?: UserObject
}
```

#### `getCurrentUser()`
Получение текущего авторизованного пользователя из памяти или localStorage.

#### `hasRole(role)`
Проверка роли пользователя.

#### `isAdmin()` / `isInstructor()`
Проверка конкретных ролей.

#### `updateProfile(userId, updates)`
Обновление профиля пользователя.

**Параметры**:
- `userId` (UUID) - ID пользователя
- `updates` (object) - объект с полями для обновления

---

### 2. UserProfileService (`src/services/userProfile.js`)

**Назначение**: Управление профилями пользователей, курсами и статистикой

**Зависимости**:
- `@supabase/supabase-js`

**Основные методы**:

#### `getProfile(userId)`
Получение полного профиля пользователя (объединяет данные из `users` и `user_profiles`).

**Возвращает**:
```javascript
{
  success: boolean,
  data?: {
    id: UUID,
    username: string,
    full_name: string,
    email: string,
    role: string,
    avatar_url: string,
    company: string,
    position: string,
    phone: string,
    bio: string,
    language: string,
    email_notifications: boolean,
    push_notifications: boolean,
    weekly_report: boolean
  }
}
```

#### `saveProfile(userId, profileData)`
Сохранение профиля пользователя (обновляет `users` и `user_profiles`).

#### `uploadAvatar(userId, file)`
Загрузка аватара пользователя в Supabase Storage.

**Логика**:
1. Валидация файла (тип, размер до 5MB)
2. Генерация уникального имени файла
3. Удаление старого аватара (если есть)
4. Загрузка в bucket `avatars`
5. Обновление `avatar_url` в `user_profiles`
6. Fallback на base64 если Storage недоступен

#### `getUserCourses(userId)`
Получение списка курсов пользователя с прогрессом.

#### `enrollInCourse(userId, courseId)`
Запись пользователя на курс.

#### `updateCourseProgress(userId, courseId, progress)`
Обновление прогресса прохождения курса.

#### `getUserStats(userId)`
Получение статистики пользователя (активные курсы, завершенные, часы обучения, сертификаты).

#### `updateUserStats(userId)`
Пересчет статистики пользователя на основе данных из `user_courses` и `certificates`.

#### `getCertificates(userId)`
Получение списка сертификатов пользователя.

---

### 3. MinIOService (`src/services/minioService.js`)

**Назначение**: Работа с MinIO для загрузки и получения файлов (PDF, видео, документы)

**Зависимости**:
- `@aws-sdk/client-s3`
- `@aws-sdk/s3-request-presigner`

**Конфигурация**:
```javascript
{
  endpoint: 'https://minio.dmed.gubkin.uz',
  bucket: 'atgedu',
  accessKey: 'admin',
  secretKey: '1234bobur$'
}
```

**Основные методы**:

#### `getPresignedDownloadUrl(objectName, expiresIn, contentType, range)`
Получение presigned URL для скачивания файла.

**Параметры**:
- `objectName` (string) - путь к файлу в MinIO
- `expiresIn` (number) - время жизни URL в секундах (по умолчанию 7 дней)
- `contentType` (string, optional) - MIME тип файла
- `range` (string, optional) - диапазон байтов для Range requests

**Особенности**:
- Кэширование URL (TTL 6 часов)
- Поддержка Range requests для streaming
- Автоматическая прокси-замена в dev режиме

#### `uploadFile(file, folder)`
Загрузка файла в MinIO.

**Возвращает**:
```javascript
{
  success: boolean,
  url: string,
  objectName: string,
  fileName: string,
  originalName: string,
  size: number,
  type: string,
  sizeFormatted: string
}
```

#### `listFiles(folder)`
Получение списка файлов в папке.

#### `getFolderContents(folderPath)`
Получение содержимого папки (файлы + подпапки).

#### `deleteFile(objectName)`
Удаление файла из MinIO.

#### `getFileMetadata(objectName)`
Получение метаданных файла (размер, тип, дата изменения).

#### `fileExists(objectName)`
Проверка существования файла.

#### `formatFileSize(bytes)`
Форматирование размера файла (мемоизированная функция).

**Кэширование**:
- URL кэш: 100 записей, TTL 6 часов
- Метаданные: 200 записей, TTL 10 минут
- Списки файлов: 50 записей, TTL 5 минут

---

### 4. VideoService (`src/services/videoService.js`)

**Назначение**: Управление видео контентом

**Зависимости**:
- `@supabase/supabase-js`

**Основные методы**:

#### `uploadVideo(file, lessonId)`
Загрузка видео в Supabase Storage (bucket `videos`).

#### `getVideoUrl(lessonId)`
Получение URL видео по ID урока.

#### `saveProgress(userId, lessonId, progress)`
Сохранение прогресса просмотра видео.

#### `completeLesson(userId, lessonId)`
Отметка урока как завершенного.

#### `getLessonProgress(userId, lessonId)`
Получение прогресса прохождения урока.

---

### 5. PDFService (`src/services/pdfService.js`)

**Назначение**: Работа с PDF документами через PDF.js

**Зависимости**:
- `pdfjs-dist`

**Основные методы**:

#### `loadPdfDocument(url)`
Загрузка PDF документа с поддержкой Range requests и кэширования.

**Особенности**:
- Кэширование документов (10 записей, TTL 30 минут)
- Поддержка streaming через Range requests
- Автоматическая загрузка только необходимых частей файла

#### `getPdfPage(pdf, pageNumber)`
Получение страницы PDF с кэшированием.

**Кэш страниц**: 50 записей

#### `renderPdfPage(page, canvas, scale)`
Отрисовка страницы PDF на canvas.

**Особенности**:
- Поддержка поворота страниц
- Оптимизация масштаба
- Очистка canvas перед отрисовкой

#### `calculateOptimalScale(page, containerWidth)`
Вычисление оптимального масштаба для отображения PDF.

---

## 🗄️ Структура базы данных

### Основные таблицы

#### 1. `users`
Основная таблица пользователей.

**Поля**:
- `id` (UUID, PK) - уникальный идентификатор
- `username` (VARCHAR(50), UNIQUE) - имя пользователя
- `password_hash` (VARCHAR(255)) - хеш пароля
- `full_name` (VARCHAR(100)) - полное имя
- `email` (VARCHAR(100)) - email
- `role` (VARCHAR(20)) - роль: 'admin', 'user', 'instructor'
- `is_active` (BOOLEAN) - активен ли пользователь
- `created_at` (TIMESTAMPTZ) - дата создания
- `updated_at` (TIMESTAMPTZ) - дата обновления

#### 2. `user_sessions`
Сессии пользователей.

**Поля**:
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `session_token` (VARCHAR(255), UNIQUE)
- `expires_at` (TIMESTAMPTZ)
- `created_at` (TIMESTAMPTZ)
- `last_activity` (TIMESTAMPTZ)
- `ip_address` (INET)
- `user_agent` (TEXT)

#### 3. `user_profiles`
Расширенные данные профиля.

**Поля**:
- `id` (UUID, PK, FK → users.id)
- `full_name` (VARCHAR(255))
- `email` (VARCHAR(255))
- `avatar_url` (TEXT)
- `company` (VARCHAR(255))
- `position` (VARCHAR(255))
- `phone` (VARCHAR(50))
- `bio` (TEXT)
- `language` (VARCHAR(10))
- `email_notifications` (BOOLEAN)
- `push_notifications` (BOOLEAN)
- `weekly_report` (BOOLEAN)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

#### 4. `stations`
Компрессорные станции.

**Поля**:
- `id` (INTEGER, PK, AUTO_INCREMENT)
- `name` (VARCHAR(255)) - полное название
- `short_name` (VARCHAR(50), UNIQUE) - краткое название (WKC1, WKC2)
- `description` (TEXT)
- `image` (VARCHAR(255))
- `tech_map_image` (VARCHAR(500))
- `power` (VARCHAR(100))
- `commission_date` (VARCHAR(20))
- `courses_count` (INTEGER) - количество курсов
- `status` (VARCHAR(20)) - 'active' | 'maintenance'
- `location` (TEXT)
- `type` (VARCHAR(255))
- `design_capacity` (VARCHAR(100))
- `gas_pressure` (VARCHAR(100))
- `distance_from_border` (VARCHAR(100))
- `pipeline_diameter` (VARCHAR(100))
- `input_pressure` (VARCHAR(100))
- `output_pressure` (VARCHAR(100))
- `parallel_lines` (VARCHAR(100))
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### 5. `course_programs`
Программы курсов.

**Поля**:
- `id` (INTEGER, PK)
- `station_id` (INTEGER, FK → stations.id)
- `title` (VARCHAR(500))
- `description` (TEXT)
- `duration` (VARCHAR(100))
- `topics_count` (INTEGER) - вычисляемое поле
- `lessons_count` (INTEGER) - вычисляемое поле
- `tests_count` (INTEGER) - вычисляемое поле
- `format` (VARCHAR(50)) - 'Онлайн' | 'Офлайн'
- `is_active` (BOOLEAN)
- `order_index` (INTEGER)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### 6. `lessons`
Уроки в рамках программы курса.

**Поля**:
- `id` (INTEGER, PK)
- `course_program_id` (INTEGER, FK → course_programs.id)
- `title` (VARCHAR(500))
- `duration` (VARCHAR(100))
- `topics_count` (INTEGER) - вычисляемое поле
- `order_index` (INTEGER)
- `is_active` (BOOLEAN)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### 7. `topics`
Темы в рамках урока.

**Поля**:
- `id` (INTEGER, PK)
- `lesson_id` (INTEGER, FK → lessons.id)
- `code` (VARCHAR(50)) - код темы (например, "Тема 1.1")
- `title` (VARCHAR(500))
- `duration` (VARCHAR(50))
- `order_index` (INTEGER)
- `is_active` (BOOLEAN)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### 8. `topic_files`
Файлы материалов тем (PDF, видео, документы).

**Поля**:
- `id` (INTEGER, PK)
- `topic_id` (INTEGER, FK → topics.id)
- `file_type` (ENUM) - 'main_pdf' | 'additional_video' | 'additional_document'
- `original_name` (VARCHAR(500))
- `file_size` (BIGINT)
- `size_formatted` (VARCHAR(50))
- `file_url` (VARCHAR(1000)) - presigned URL
- `minio_object_name` (VARCHAR(1000)) - путь в MinIO
- `mime_type` (VARCHAR(100))
- `is_active` (BOOLEAN)
- `order_index` (INTEGER)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Ограничения**:
- Для каждой темы может быть только один файл с `file_type = 'main_pdf'`

#### 9. `courses`
Курсы системы (для пользовательских курсов).

**Поля**:
- `id` (UUID или INTEGER, PK)
- `title` (VARCHAR(255))
- `description` (TEXT)
- `station_id` (INTEGER, FK → stations.id)
- `duration_hours` (INTEGER)
- `level` (VARCHAR(50))
- `is_active` (BOOLEAN)
- `icon` (VARCHAR(255))

#### 10. `user_courses`
Участие пользователей в курсах.

**Поля**:
- `id` (UUID или INTEGER, PK)
- `user_id` (UUID, FK → users.id)
- `course_id` (UUID/INTEGER, FK → courses.id)
- `progress_percent` (INTEGER) - 0-100
- `status` (VARCHAR(20)) - 'in_progress' | 'completed' | 'not_started'
- `started_at` (TIMESTAMPTZ)
- `completed_at` (TIMESTAMPTZ)
- `hours_studied` (NUMERIC)
- `last_activity` (TIMESTAMPTZ)

#### 11. `certificates`
Сертификаты пользователей.

**Поля**:
- `id` (UUID или INTEGER, PK)
- `user_id` (UUID, FK → users.id)
- `course_id` (UUID/INTEGER, FK → courses.id)
- `title` (VARCHAR(255))
- `issued_at` (TIMESTAMPTZ)
- `pdf_url` (TEXT)

#### 12. `user_stats`
Статистика пользователей.

**Поля**:
- `user_id` (UUID, PK, FK → users.id)
- `active_courses` (INTEGER)
- `completed_courses` (INTEGER)
- `total_hours_studied` (NUMERIC)
- `certificates_count` (INTEGER)
- `achievements` (JSONB)
- `last_updated` (TIMESTAMPTZ)

### Вспомогательные таблицы

- `station_gas_supply_sources` - источники поставки газа для станций
- `station_equipment` - оборудование станций
- `station_specifications` - технические характеристики
- `station_safety_systems` - системы безопасности
- `station_safety_system_features` - особенности систем безопасности
- `course_program_learning_outcomes` - результаты обучения
- `course_program_requirements` - требования к участникам
- `course_program_target_audience` - целевая аудитория
- `lesson_materials` - материалы уроков
- `lesson_tests` - тесты уроков
- `final_tests` - итоговые тесты

---

## 🔐 Безопасность

### Row Level Security (RLS)

В Supabase включен RLS для следующих таблиц:
- `users` - пользователи видят только свои данные
- `user_sessions` - сессии привязаны к пользователям
- `user_profiles` - профили доступны только владельцам
- `user_courses` - пользователи видят только свои курсы
- `certificates` - сертификаты доступны только владельцам

### Хранение паролей

⚠️ **Важно**: В текущей версии используется простое сравнение паролей. Для продакшена необходимо:
- Использовать bcrypt или аналогичные библиотеки
- Хранить только хеши паролей
- Никогда не передавать пароли в открытом виде

### Сессии

- Токены сессий генерируются случайно
- Время жизни сессии: 24 часа
- Отслеживается IP адрес и User Agent
- Автоматическая очистка истекших сессий

---

## 📦 Хранилище файлов

### Supabase Storage

**Buckets**:
- `avatars` - аватары пользователей (публичный доступ)
- `videos` - видео материалы (приватный доступ)

**Политики доступа**:
- Публичное чтение для аватаров
- Загрузка только для авторизованных пользователей
- Обновление/удаление только владельцем

### MinIO

**Конфигурация**:
- Endpoint: `https://minio.dmed.gubkin.uz`
- Bucket: `atgedu`
- Используется для больших файлов (PDF, видео)

**Особенности**:
- Presigned URLs для безопасного доступа
- Поддержка Range requests для streaming
- Кэширование URL и метаданных

---

## 🔄 API Endpoints (через Supabase)

Все взаимодействие с базой данных происходит через Supabase Client:

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(url, key)

// Примеры запросов:
// Получение данных
const { data, error } = await supabase
  .from('table_name')
  .select('*')
  .eq('column', 'value')

// Вставка данных
const { data, error } = await supabase
  .from('table_name')
  .insert({ ... })

// Обновление данных
const { data, error } = await supabase
  .from('table_name')
  .update({ ... })
  .eq('id', id)

// Удаление данных
const { error } = await supabase
  .from('table_name')
  .delete()
  .eq('id', id)
```

---

## 🚀 Развертывание

### Переменные окружения

Создайте файл `.env`:

```env
# Supabase
VITE_SUPABASE_URL=https://fusartgifhigtysskgfg.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here

# MinIO
VITE_MINIO_ENDPOINT=https://minio.dmed.gubkin.uz
VITE_MINIO_ACCESS_KEY=admin
VITE_MINIO_SECRET_KEY=1234bobur$
VITE_MINIO_BUCKET=atgedu
```

### Настройка Supabase

1. Создайте проект в Supabase
2. Выполните миграции (см. `migrations/`)
3. Создайте Storage buckets:
   - `avatars` (публичный)
   - `videos` (приватный)
4. Настройте RLS политики

### Настройка MinIO

1. Установите MinIO сервер
2. Создайте bucket `atgedu`
3. Настройте доступ (access key / secret key)
4. Настройте CORS для веб-приложения

---

## 📊 Мониторинг и логирование

### Логирование

Все сервисы логируют ошибки в консоль:
```javascript
console.error('Error message:', error)
```

### Кэширование

MinIOService использует LRU кэш для:
- Presigned URLs (TTL 6 часов)
- Метаданные файлов (TTL 10 минут)
- Списки файлов (TTL 5 минут)

### Статистика кэша

```javascript
import minioService from '@/services/minioService'
const stats = minioService.getCacheStats()
```

---

## 🔧 Утилиты и вспомогательные функции

### Composables (`src/composables/`)

- `useCache.js` - работа с кэшем
- `useMaterials.js` - работа с материалами
- `useNotify.js` - уведомления
- `usePdf.js` - работа с PDF
- `useProgress.js` - отслеживание прогресса
- `useVideo.js` - работа с видео

---

## 📝 Примеры использования

### Авторизация

```javascript
import authService from '@/services/auth'

// Вход
const result = await authService.login('username', 'password')
if (result.success) {
  console.log('Пользователь авторизован:', result.user)
}

// Проверка авторизации
const authResult = await authService.checkAuth()
if (authResult.isAuthenticated) {
  console.log('Пользователь авторизован')
}

// Выход
await authService.logout()
```

### Работа с профилем

```javascript
import userProfileService from '@/services/userProfile'

// Получение профиля
const profile = await userProfileService.getProfile(userId)

// Обновление профиля
await userProfileService.saveProfile(userId, {
  full_name: 'Иван Иванов',
  position: 'Инженер'
})

// Загрузка аватара
await userProfileService.uploadAvatar(userId, file)
```

### Работа с файлами (MinIO)

```javascript
import minioService from '@/services/minioService'

// Загрузка файла
const result = await minioService.uploadFile(file, 'folder')

// Получение URL
const url = await minioService.getPresignedDownloadUrl('path/to/file.pdf')

// Список файлов
const files = await minioService.listFiles('folder')
```

### Работа с PDF

```javascript
import pdfService from '@/services/pdfService'

// Загрузка документа
const pdf = await pdfService.loadPdfDocument(url)

// Получение страницы
const page = await pdfService.getPdfPage(pdf, 1)

// Отрисовка на canvas
await pdfService.renderPdfPage(page, canvas, 2.0)
```

---

## 🐛 Отладка

### Проверка подключения к Supabase

```javascript
const { data, error } = await supabase
  .from('users')
  .select('count')
```

### Проверка подключения к MinIO

```javascript
import minioService from '@/services/minioService'
try {
  const files = await minioService.listFiles()
  console.log('MinIO подключен:', files)
} catch (error) {
  console.error('Ошибка MinIO:', error)
}
```

### Очистка кэша

```javascript
import minioService from '@/services/minioService'
minioService.clearCache()
```

---

## 📚 Дополнительные ресурсы

- [Документация Supabase](https://supabase.com/docs)
- [Документация MinIO](https://min.io/docs)
- [Документация AWS SDK S3](https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/s3-examples.html)
- [Документация PDF.js](https://mozilla.github.io/pdf.js/)

---

**Версия документации**: 1.0  
**Дата обновления**: 2025-01-23  
**Автор**: ATG Education Development Team

