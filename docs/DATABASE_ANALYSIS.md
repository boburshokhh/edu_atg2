# Анализ базы данных PostgreSQL (atg_edu)

**Дата анализа:** 2025-01-27  
**База данных:** atg_edu  
**Хост:** 192.168.32.100:5432

---

## 📊 Общая структура базы данных

База данных содержит **28 таблиц**, **3 функции** и **11 триггеров**.

---

## 🗂️ Структура таблиц

### 1. **Пользователи и аутентификация**

#### `users` - Основная таблица пользователей
- `id` (uuid, PK) - Уникальный идентификатор
- `username` (varchar(50), UNIQUE, NOT NULL) - Имя пользователя
- `password_hash` (varchar(255), NOT NULL) - Хеш пароля
- `full_name` (varchar(100)) - Полное имя
- `email` (varchar(100)) - Email
- `role` (varchar(20), CHECK: 'admin', 'user', 'instructor') - Роль пользователя
- `is_active` (boolean, default: true) - Активен ли пользователь
- `created_at` (timestamptz, default: now())
- `updated_at` (timestamptz, default: now())

#### `user_profiles` - Профили пользователей
- `id` (uuid, PK, FK → users.id) - Связь с users
- `full_name` (varchar(255)) - Полное имя
- `email` (varchar(255)) - Email
- `avatar_url` (text) - URL аватара
- `company` (varchar(255)) - Компания
- `position` (varchar(255)) - Должность
- `phone` (varchar(50)) - Телефон
- `bio` (text) - Биография
- `language` (varchar(10), default: 'ru') - Язык интерфейса
- `email_notifications` (boolean, default: true)
- `push_notifications` (boolean, default: false)
- `weekly_report` (boolean, default: true)
- `created_at`, `updated_at` (timestamptz)

#### `user_sessions` - Сессии пользователей
- `id` (uuid, PK)
- `user_id` (uuid, FK → users.id, NOT NULL)
- `session_token` (varchar(255), UNIQUE, NOT NULL)
- `expires_at` (timestamptz, NOT NULL)
- `created_at`, `last_activity` (timestamptz)
- `ip_address` (inet)
- `user_agent` (text)

#### `user_stats` - Статистика пользователей
- `user_id` (uuid, PK, FK → users.id)
- `active_courses` (integer, default: 0)
- `completed_courses` (integer, default: 0)
- `total_hours_studied` (numeric, default: 0)
- `certificates_count` (integer, default: 0)
- `achievements` (jsonb, default: '[]')
- `last_updated` (timestamptz, default: now())

---

### 2. **Станции (Stations)**

#### `stations` - Компрессорные станции
- `id` (integer, PK, SERIAL)
- `name` (varchar(255), NOT NULL) - Название станции
- `short_name` (varchar(50), UNIQUE, NOT NULL) - Короткое название
- `description` (text) - Описание
- `image` (varchar(255)) - Изображение
- `tech_map_image` (varchar(500)) - Техническая карта
- `power` (varchar(100)) - Мощность
- `commission_date` (varchar(20)) - Дата ввода в эксплуатацию
- `courses_count` (integer, default: 0)
- `status` (varchar(20), CHECK: 'active', 'maintenance', default: 'active')
- `location` (text) - Местоположение
- `type` (varchar(255)) - Тип станции
- `design_capacity` (varchar(100)) - Проектная мощность
- `gas_pressure` (varchar(100)) - Давление газа
- `distance_from_border` (varchar(100)) - Расстояние от границы
- `pipeline_diameter` (varchar(100)) - Диаметр трубопровода
- `input_pressure` (varchar(100)) - Входное давление
- `output_pressure` (varchar(100)) - Выходное давление
- `parallel_lines` (varchar(100)) - Параллельные линии
- `created_at`, `updated_at` (timestamp)

#### `station_specifications` - Спецификации станций
- `id` (integer, PK, SERIAL)
- `station_id` (integer, FK → stations.id, NOT NULL)
- `category` (varchar(255), NOT NULL) - Категория спецификации
- `value` (varchar(100)) - Значение
- `unit` (varchar(50)) - Единица измерения
- `description` (text) - Описание
- `order_index` (integer, default: 0)
- `created_at` (timestamp)

#### `station_equipment` - Оборудование станций
- `id` (integer, PK, SERIAL)
- `station_id` (integer, FK → stations.id, NOT NULL)
- `name` (varchar(255), NOT NULL) - Название оборудования
- `model` (varchar(255)) - Модель
- `manufacturer` (varchar(255)) - Производитель
- `quantity` (integer, default: 1) - Количество
- `power` (varchar(100)) - Мощность
- `description` (text) - Описание
- `order_index` (integer, default: 0)
- `created_at` (timestamp)

#### `station_gas_supply_sources` - Источники газоснабжения
- `id` (integer, PK, SERIAL)
- `station_id` (integer, FK → stations.id, NOT NULL)
- `source_name` (varchar(255), NOT NULL) - Название источника
- `order_index` (integer, default: 0)
- `created_at` (timestamp)

#### `station_safety_systems` - Системы безопасности
- `id` (integer, PK, SERIAL)
- `station_id` (integer, FK → stations.id, NOT NULL)
- `name` (varchar(255), NOT NULL) - Название системы
- `description` (text) - Описание
- `manufacturer` (varchar(255)) - Производитель
- `order_index` (integer, default: 0)
- `created_at` (timestamp)

#### `station_safety_system_features` - Характеристики систем безопасности
- `id` (integer, PK, SERIAL)
- `safety_system_id` (integer, FK → station_safety_systems.id, NOT NULL)
- `feature_name` (varchar(255), NOT NULL) - Название характеристики
- `order_index` (integer, default: 0)
- `created_at` (timestamp)

---

### 3. **Курсы и программы обучения**

#### `courses` - Курсы
- `id` (uuid, PK, default: gen_random_uuid())
- `title` (varchar(255), NOT NULL) - Название курса
- `description` (text) - Описание
- `station_id` (integer, FK → stations.id) - Связь со станцией
- `duration_hours` (integer, default: 0) - Продолжительность в часах
- `level` (varchar(50), default: 'beginner') - Уровень сложности
- `is_active` (boolean, default: true) - Активен ли курс
- `icon` (varchar(255)) - Иконка
- `created_at`, `updated_at` (timestamptz)

#### `course_programs` - Программы курсов
- `id` (integer, PK, SERIAL)
- `station_id` (integer, FK → stations.id, NOT NULL)
- `title` (varchar(500), NOT NULL) - Название программы
- `description` (text) - Описание
- `duration` (varchar(100)) - Продолжительность
- `topics_count` (integer, default: 0) - Количество тем
- `lessons_count` (integer, default: 0) - Количество уроков
- `tests_count` (integer, default: 0) - Количество тестов
- `format` (varchar(50), default: 'Онлайн') - Формат обучения
- `is_active` (boolean, default: true)
- `order_index` (integer, default: 0)
- `created_at`, `updated_at` (timestamp)

#### `course_program_learning_outcomes` - Результаты обучения
- `id` (integer, PK, SERIAL)
- `course_program_id` (integer, FK → course_programs.id, NOT NULL)
- `outcome_text` (text, NOT NULL) - Текст результата
- `order_index` (integer, default: 0)
- `created_at` (timestamp)

#### `course_program_requirements` - Требования к программе
- `id` (integer, PK, SERIAL)
- `course_program_id` (integer, FK → course_programs.id, NOT NULL)
- `requirement_text` (text, NOT NULL) - Текст требования
- `order_index` (integer, default: 0)
- `created_at` (timestamp)

#### `course_program_target_audience` - Целевая аудитория
- `id` (integer, PK, SERIAL)
- `course_program_id` (integer, FK → course_programs.id, NOT NULL)
- `audience_text` (varchar(255), NOT NULL) - Описание аудитории
- `order_index` (integer, default: 0)
- `created_at` (timestamp)

#### `user_courses` - Курсы пользователей
- `id` (uuid, PK, default: gen_random_uuid())
- `user_id` (uuid, FK → users.id) - Пользователь
- `course_id` (uuid, FK → courses.id) - Курс
- `progress_percent` (integer, CHECK: 0-100, default: 0) - Прогресс в процентах
- `status` (varchar(20), CHECK: 'not_started', 'in_progress', 'completed', default: 'in_progress')
- `started_at` (timestamptz, default: now())
- `completed_at` (timestamptz) - Дата завершения
- `hours_studied` (numeric, default: 0) - Часов изучено
- `last_activity` (timestamptz, default: now())
- UNIQUE(user_id, course_id) - Один курс на пользователя

---

### 4. **Уроки и темы**

#### `lessons` - Уроки
- `id` (uuid, PK, default: gen_random_uuid())
- `course_id` (uuid, FK → courses.id) - Связь с курсом
- `title` (varchar(255), NOT NULL) - Название урока
- `description` (text) - Описание
- `video_url` (text) - URL видео
- `duration_minutes` (integer, default: 0) - Продолжительность в минутах
- `lesson_order` (integer, default: 0) - Порядок урока
- `lesson_type` (varchar(50), default: 'video') - Тип урока
- `is_free` (boolean, default: false) - Бесплатный ли урок
- `content` (text) - Содержание
- `resources` (jsonb, default: '[]') - Ресурсы в формате JSON
- `created_at`, `updated_at` (timestamptz)

#### `topics` - Темы уроков
- `id` (integer, PK, SERIAL)
- `lesson_id` (uuid, FK → lessons.id) - Связь с уроком
- `code` (varchar(50)) - Код темы
- `title` (varchar(500), NOT NULL) - Название темы
- `duration` (varchar(50)) - Продолжительность
- `order_index` (integer, NOT NULL, default: 0) - Порядок темы
- `is_active` (boolean, default: true)
- `created_at`, `updated_at` (timestamp)

#### `topic_files` - Файлы тем
- `id` (integer, PK, SERIAL)
- `topic_id` (integer, FK → topics.id, NOT NULL)
- `file_type` (varchar(50), NOT NULL, CHECK: 'main_pdf', 'additional_video', 'additional_document')
- `original_name` (varchar(500), NOT NULL) - Оригинальное имя файла
- `file_size` (bigint) - Размер файла
- `size_formatted` (varchar(50)) - Форматированный размер
- `file_url` (varchar(1000)) - URL файла
- `minio_object_name` (varchar(1000), NOT NULL) - Имя объекта в MinIO
- `mime_type` (varchar(100)) - MIME тип
- `is_active` (boolean, default: true)
- `order_index` (integer, default: 0)
- `created_at`, `updated_at` (timestamp)
- UNIQUE(topic_id, file_type) WHERE file_type = 'main_pdf' - Один основной PDF на тему

#### `lesson_materials` - Материалы уроков
- `id` (integer, PK, SERIAL)
- `lesson_id` (uuid, FK → lessons.id, NOT NULL)
- `material_name` (varchar(255), NOT NULL) - Название материала
- `order_index` (integer, default: 0)
- `created_at` (timestamp)

#### `lesson_progress` - Прогресс изучения уроков
- `id` (uuid, PK, default: gen_random_uuid())
- `user_id` (uuid, FK → users.id) - Пользователь
- `lesson_id` (uuid, FK → lessons.id) - Урок
- `progress_percent` (integer, default: 0) - Прогресс в процентах
- `watch_time_seconds` (integer, default: 0) - Время просмотра в секундах
- `last_position_seconds` (integer, default: 0) - Последняя позиция просмотра
- `completed` (boolean, default: false) - Завершен ли урок
- `completed_at` (timestamptz) - Дата завершения
- `last_activity` (timestamptz, default: now()) - Последняя активность
- UNIQUE(user_id, lesson_id) - Один прогресс на пользователя и урок

---

### 5. **Тесты**

#### `tests` - Тесты
- `id` (varchar(100), PK) - Идентификатор теста
- `lesson_id` (uuid, FK → lessons.id) - Связь с уроком
- `lesson_index` (integer) - Индекс урока
- `topic_index` (integer) - Индекс темы
- `title` (varchar(500), NOT NULL) - Название теста
- `description` (text) - Описание
- `time_limit` (integer) - Ограничение времени в секундах
- `passing_score` (integer) - Проходной балл
- `attempts` (integer, default: 3) - Количество попыток
- `is_final_test` (boolean, default: false) - Финальный ли тест
- `created_at`, `updated_at` (timestamptz)

#### `lesson_tests` - Тесты уроков
- `id` (integer, PK, SERIAL)
- `lesson_id` (uuid, FK → lessons.id, NOT NULL)
- `title` (varchar(500), NOT NULL) - Название теста
- `questions_count` (integer, default: 0) - Количество вопросов
- `is_active` (boolean, default: true)
- `created_at`, `updated_at` (timestamp)

#### `final_tests` - Финальные тесты
- `id` (integer, PK, SERIAL)
- `course_program_id` (integer, FK → course_programs.id, NOT NULL)
- `title` (varchar(500), NOT NULL) - Название теста
- `questions_count` (integer, default: 0) - Количество вопросов
- `is_active` (boolean, default: true)
- `created_at`, `updated_at` (timestamp)

#### `test_questions` - Вопросы тестов
- `id` (integer, PK, SERIAL)
- `test_id` (varchar(100), FK → tests.id, NOT NULL)
- `question_text` (text, NOT NULL) - Текст вопроса
- `options` (jsonb, NOT NULL) - Варианты ответов в формате JSON
- `correct_answer` (integer, NOT NULL) - Индекс правильного ответа
- `points` (integer, default: 1) - Баллы за вопрос
- `explanation` (text) - Объяснение ответа
- `order_index` (integer, default: 0) - Порядок вопроса
- `created_at` (timestamptz)

#### `test_attempts` - Попытки прохождения тестов
- `id` (uuid, PK, default: gen_random_uuid())
- `user_id` (uuid, FK → users.id, NOT NULL) - Пользователь
- `test_id` (varchar(100), FK → tests.id, NOT NULL) - Тест
- `score` (integer, default: 0) - Набранные баллы
- `max_score` (integer, default: 0) - Максимальные баллы
- `passed` (boolean, default: false) - Пройден ли тест
- `time_spent_seconds` (integer, default: 0) - Время прохождения в секундах
- `answers` (jsonb, default: '[]') - Ответы в формате JSON
- `started_at` (timestamptz, default: now())
- `completed_at` (timestamptz) - Дата завершения
- `created_at` (timestamptz)

---

### 6. **Сертификаты**

#### `certificates` - Сертификаты
- `id` (uuid, PK, default: gen_random_uuid())
- `user_id` (uuid, FK → users.id) - Пользователь
- `course_id` (uuid, FK → courses.id) - Курс
- `title` (varchar(255), NOT NULL) - Название сертификата
- `issued_at` (timestamptz, default: now()) - Дата выдачи
- `pdf_url` (text) - URL PDF сертификата

---

### 7. **Сотрудники**

#### `employees` - Сотрудники
- `id` (integer, PK, SERIAL)
- `name` (varchar(100)) - Имя
- `email` (varchar(100), UNIQUE) - Email
- `department` (varchar(50)) - Отдел
- `created_at` (timestamp)

---

## 🔧 Функции базы данных

### 1. `cleanup_expired_sessions()`
**Тип:** VOLATILE  
**Возвращает:** INTEGER  
**Язык:** plpgsql  
**Безопасность:** SECURITY DEFINER

**Описание:** Удаляет истекшие сессии пользователей из таблицы `user_sessions`.

**Код:**
```sql
CREATE OR REPLACE FUNCTION public.cleanup_expired_sessions()
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $function$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$function$
```

**Использование:** Периодическая очистка истекших сессий (можно вызывать через cron job).

---

### 2. `set_current_user(user_id uuid)`
**Тип:** VOLATILE  
**Возвращает:** VOID  
**Язык:** plpgsql  
**Безопасность:** SECURITY DEFINER

**Описание:** Устанавливает текущего пользователя в переменную сессии для использования в функциях аутентификации (например, `auth.uid()`).

**Параметры:**
- `user_id` (uuid) - ID пользователя

**Код:**
```sql
CREATE OR REPLACE FUNCTION public.set_current_user(user_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $function$
BEGIN
    -- Устанавливаем переменную сессии для использования в auth.uid()
    PERFORM set_config('app.current_user_id', user_id::TEXT, false);
END;
$function$
```

**Использование:** Установка контекста пользователя для RLS (Row Level Security) политик.

---

### 3. `update_updated_at_column()`
**Тип:** VOLATILE  
**Возвращает:** TRIGGER  
**Язык:** plpgsql  
**Безопасность:** SECURITY DEFINER

**Описание:** Триггерная функция для автоматического обновления поля `updated_at` при изменении записи. Поддерживает разные типы временных меток для разных таблиц.

**Код:**
```sql
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $function$
BEGIN
    -- Автоматически определяет тип поля и устанавливает соответствующее значение
    IF TG_TABLE_NAME IN ('stations', 'course_programs', 'topics', 'topic_files',
                          'lesson_tests', 'final_tests') THEN
        NEW.updated_at = CURRENT_TIMESTAMP::TIMESTAMP;
    ELSE
        NEW.updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$function$
```

**Использование:** Автоматическое обновление временных меток в следующих таблицах:
- `stations`
- `course_programs`
- `topics`
- `topic_files`
- `lesson_tests`
- `final_tests`
- `courses`
- `lessons`
- `tests`
- `user_profiles`
- `users`

---

## ⚡ Триггеры

Всего **11 триггеров**, все используют функцию `update_updated_at_column()` для автоматического обновления поля `updated_at`:

1. `update_course_programs_updated_at` - на таблице `course_programs`
2. `update_courses_updated_at` - на таблице `courses`
3. `update_final_tests_updated_at` - на таблице `final_tests`
4. `update_lesson_tests_updated_at` - на таблице `lesson_tests`
5. `update_lessons_updated_at` - на таблице `lessons`
6. `update_stations_updated_at` - на таблице `stations`
7. `update_tests_updated_at` - на таблице `tests`
8. `update_topic_files_updated_at` - на таблице `topic_files`
9. `update_topics_updated_at` - на таблице `topics`
10. `update_user_profiles_updated_at` - на таблице `user_profiles`
11. `update_users_updated_at` - на таблице `users`

**Тип:** BEFORE UPDATE  
**Уровень:** ROW  
**Событие:** UPDATE

---

## 🔗 Связи между таблицами (Foreign Keys)

### Основные связи:

1. **Пользователи:**
   - `user_profiles.id` → `users.id`
   - `user_sessions.user_id` → `users.id`
   - `user_stats.user_id` → `users.id`
   - `user_courses.user_id` → `users.id`
   - `lesson_progress.user_id` → `users.id`
   - `test_attempts.user_id` → `users.id`
   - `certificates.user_id` → `users.id`

2. **Станции:**
   - `courses.station_id` → `stations.id`
   - `course_programs.station_id` → `stations.id`
   - `station_specifications.station_id` → `stations.id`
   - `station_equipment.station_id` → `stations.id`
   - `station_gas_supply_sources.station_id` → `stations.id`
   - `station_safety_systems.station_id` → `stations.id`

3. **Курсы:**
   - `lessons.course_id` → `courses.id`
   - `user_courses.course_id` → `courses.id`
   - `certificates.course_id` → `courses.id`

4. **Уроки:**
   - `topics.lesson_id` → `lessons.id`
   - `lesson_materials.lesson_id` → `lessons.id`
   - `lesson_progress.lesson_id` → `lessons.id`
   - `lesson_tests.lesson_id` → `lessons.id`
   - `tests.lesson_id` → `lessons.id`

5. **Темы:**
   - `topic_files.topic_id` → `topics.id`

6. **Программы курсов:**
   - `course_program_learning_outcomes.course_program_id` → `course_programs.id`
   - `course_program_requirements.course_program_id` → `course_programs.id`
   - `course_program_target_audience.course_program_id` → `course_programs.id`
   - `final_tests.course_program_id` → `course_programs.id`

7. **Тесты:**
   - `test_questions.test_id` → `tests.id`
   - `test_attempts.test_id` → `tests.id`

8. **Системы безопасности:**
   - `station_safety_system_features.safety_system_id` → `station_safety_systems.id`

---

## 📝 Особенности структуры

### Типы данных:
- **UUID** используется для: `users`, `courses`, `lessons`, `certificates`, `user_courses`, `lesson_progress`, `test_attempts`, `user_sessions`
- **INTEGER (SERIAL)** используется для: `stations`, `course_programs`, `topics`, `topic_files`, и других связанных таблиц
- **JSONB** используется для: `lessons.resources`, `test_attempts.answers`, `test_questions.options`, `user_stats.achievements`

### Ограничения (Constraints):
- **CHECK constraints** для валидации значений:
  - `users.role`: 'admin', 'user', 'instructor'
  - `stations.status`: 'active', 'maintenance'
  - `user_courses.status`: 'not_started', 'in_progress', 'completed'
  - `user_courses.progress_percent`: 0-100
  - `topic_files.file_type`: 'main_pdf', 'additional_video', 'additional_document'

- **UNIQUE constraints**:
  - `users.username`
  - `stations.short_name`
  - `employees.email`
  - `user_sessions.session_token`
  - `user_courses(user_id, course_id)`
  - `lesson_progress(user_id, lesson_id)`
  - `topic_files(topic_id, file_type)` для main_pdf

### Индексы:
- Все PRIMARY KEY автоматически создают индексы
- Все UNIQUE constraints создают индексы
- Foreign Keys могут иметь индексы для оптимизации JOIN операций

---

## 🎯 Рекомендации по оптимизации

1. **Индексы:**
   - Добавить индексы на часто используемые поля для поиска:
     - `users.email`
     - `courses.station_id`
     - `lessons.course_id`
     - `topics.lesson_id`
     - `test_attempts.user_id`, `test_attempts.test_id`
     - `lesson_progress.user_id`, `lesson_progress.lesson_id`

2. **Партиционирование:**
   - Рассмотреть партиционирование больших таблиц:
     - `test_attempts` (по дате создания)
     - `user_sessions` (по дате истечения)

3. **Очистка данных:**
   - Настроить регулярный вызов `cleanup_expired_sessions()` для очистки истекших сессий
   - Рассмотреть архивацию старых записей `test_attempts`

4. **Мониторинг:**
   - Отслеживать размер таблиц и производительность запросов
   - Анализировать использование индексов

---

## 📊 Статистика базы данных

- **Всего таблиц:** 28
- **Всего функций:** 3
- **Всего триггеров:** 11
- **Всего ограничений:** ~150+ (PK, FK, UNIQUE, CHECK)

---

*Документ создан автоматически на основе анализа структуры базы данных через PostgreSQL MCP.*

