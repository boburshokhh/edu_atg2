# Схема базы данных для управления курсами станций

## Обзор

Данный документ описывает структуру базы данных для системы управления обучающими курсами компрессорных станций. Схема позволяет управлять всей информацией о станциях, курсах, уроках, темах и учебных материалах через административную панель.

---

## Таблицы базы данных

### 1. `stations` - Станции

Основная информация о компрессорных станциях.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `name` | VARCHAR(255) | Полное наименование станции | NOT NULL |
| `short_name` | VARCHAR(50) | Краткое название (WKC1, WKC2 и т.д.) | NOT NULL, UNIQUE |
| `description` | TEXT | Описание станции | |
| `image` | VARCHAR(255) | Имя файла изображения станции | |
| `tech_map_image` | VARCHAR(500) | Путь к технологической карте | |
| `power` | VARCHAR(100) | Мощность станции | |
| `commission_date` | VARCHAR(20) | Дата ввода в эксплуатацию | |
| `courses_count` | INTEGER | Количество курсов (вычисляемое) | DEFAULT 0 |
| `status` | VARCHAR(20) | Статус (active/maintenance) | DEFAULT 'active' |
| `location` | TEXT | Местоположение станции | |
| `type` | VARCHAR(255) | Тип станции | |
| `design_capacity` | VARCHAR(100) | Проектная мощность | |
| `gas_pressure` | VARCHAR(100) | Давление газа | |
| `distance_from_border` | VARCHAR(100) | Расстояние от границы | |
| `pipeline_diameter` | VARCHAR(100) | Диаметр трубопровода | |
| `input_pressure` | VARCHAR(100) | Входное давление | |
| `output_pressure` | VARCHAR(100) | Выходное давление | |
| `parallel_lines` | VARCHAR(100) | Параллельные нитки | |
| `created_at` | TIMESTAMP | Дата создания записи | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата последнего обновления | DEFAULT NOW() ON UPDATE NOW() |

**Индексы:**
- `idx_stations_short_name` на `short_name`
- `idx_stations_status` на `status`

---

### 2. `station_gas_supply_sources` - Источники поставки газа

Связь многие-ко-многим между станциями и источниками газа.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `station_id` | INTEGER | ID станции | FOREIGN KEY → stations(id) ON DELETE CASCADE |
| `source_name` | VARCHAR(255) | Название источника | NOT NULL |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_gas_sources_station` на `station_id`

---

### 3. `station_equipment` - Оборудование станций

Список оборудования для каждой станции.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `station_id` | INTEGER | ID станции | FOREIGN KEY → stations(id) ON DELETE CASCADE |
| `name` | VARCHAR(255) | Наименование оборудования | NOT NULL |
| `model` | VARCHAR(255) | Модель/тип | |
| `manufacturer` | VARCHAR(255) | Производитель | |
| `quantity` | INTEGER | Количество единиц | DEFAULT 1 |
| `power` | VARCHAR(100) | Мощность | |
| `description` | TEXT | Описание оборудования | |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_equipment_station` на `station_id`

---

### 4. `station_specifications` - Технические характеристики

Технические характеристики станций.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `station_id` | INTEGER | ID станции | FOREIGN KEY → stations(id) ON DELETE CASCADE |
| `category` | VARCHAR(255) | Название параметра | NOT NULL |
| `value` | VARCHAR(100) | Значение | |
| `unit` | VARCHAR(50) | Единица измерения | |
| `description` | TEXT | Описание параметра | |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_specs_station` на `station_id`

---

### 5. `station_safety_systems` - Системы безопасности

Системы безопасности и контроля станций.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `station_id` | INTEGER | ID станции | FOREIGN KEY → stations(id) ON DELETE CASCADE |
| `name` | VARCHAR(255) | Название системы | NOT NULL |
| `description` | TEXT | Описание системы | |
| `manufacturer` | VARCHAR(255) | Производитель | |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_safety_station` на `station_id`

---

### 6. `station_safety_system_features` - Особенности систем безопасности

Особенности/функции систем безопасности.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `safety_system_id` | INTEGER | ID системы безопасности | FOREIGN KEY → station_safety_systems(id) ON DELETE CASCADE |
| `feature_name` | VARCHAR(255) | Название особенности | NOT NULL |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_features_safety` на `safety_system_id`

---

### 7. `course_programs` - Программы курсов

Основная информация о программах обучения для станций.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `station_id` | INTEGER | ID станции | FOREIGN KEY → stations(id) ON DELETE CASCADE |
| `title` | VARCHAR(500) | Название программы | NOT NULL |
| `description` | TEXT | Описание программы | |
| `duration` | VARCHAR(100) | Продолжительность (например, "10 академических часов") | |
| `topics_count` | INTEGER | Количество тем (вычисляемое) | DEFAULT 0 |
| `lessons_count` | INTEGER | Количество уроков (вычисляемое) | DEFAULT 0 |
| `tests_count` | INTEGER | Количество тестов (вычисляемое) | DEFAULT 0 |
| `format` | VARCHAR(50) | Формат обучения (Онлайн/Офлайн) | DEFAULT 'Онлайн' |
| `is_active` | BOOLEAN | Активна ли программа | DEFAULT true |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата обновления | DEFAULT NOW() ON UPDATE NOW() |

**Индексы:**
- `idx_courses_station` на `station_id`
- `idx_courses_active` на `is_active`

---

### 8. `course_program_learning_outcomes` - Результаты обучения

Ожидаемые результаты обучения программы.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `course_program_id` | INTEGER | ID программы курса | FOREIGN KEY → course_programs(id) ON DELETE CASCADE |
| `outcome_text` | TEXT | Текст результата обучения | NOT NULL |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_outcomes_course` на `course_program_id`

---

### 9. `course_program_requirements` - Требования к участникам

Требования к участникам программы обучения.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `course_program_id` | INTEGER | ID программы курса | FOREIGN KEY → course_programs(id) ON DELETE CASCADE |
| `requirement_text` | TEXT | Текст требования | NOT NULL |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_requirements_course` на `course_program_id`

---

### 10. `course_program_target_audience` - Целевая аудитория

Целевая аудитория программы обучения.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `course_program_id` | INTEGER | ID программы курса | FOREIGN KEY → course_programs(id) ON DELETE CASCADE |
| `audience_text` | VARCHAR(255) | Описание аудитории | NOT NULL |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_audience_course` на `course_program_id`

---

### 11. `lessons` - Уроки

Уроки в рамках программы курса.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `course_program_id` | INTEGER | ID программы курса | FOREIGN KEY → course_programs(id) ON DELETE CASCADE |
| `title` | VARCHAR(500) | Название урока | NOT NULL |
| `duration` | VARCHAR(100) | Продолжительность урока | |
| `topics_count` | INTEGER | Количество тем (вычисляемое) | DEFAULT 0 |
| `order_index` | INTEGER | Порядок урока в программе | NOT NULL, DEFAULT 0 |
| `is_active` | BOOLEAN | Активен ли урок | DEFAULT true |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата обновления | DEFAULT NOW() ON UPDATE NOW() |

**Индексы:**
- `idx_lessons_course` на `course_program_id`
- `idx_lessons_order` на `(course_program_id, order_index)`

---

### 12. `lesson_materials` - Дополнительные материалы урока

Рекомендуемые материалы для урока.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `lesson_id` | INTEGER | ID урока | FOREIGN KEY → lessons(id) ON DELETE CASCADE |
| `material_name` | VARCHAR(255) | Название материала | NOT NULL |
| `order_index` | INTEGER | Порядок отображения | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_materials_lesson` на `lesson_id`

---

### 13. `lesson_tests` - Тесты для уроков

Тестовые задания для уроков.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `lesson_id` | INTEGER | ID урока | FOREIGN KEY → lessons(id) ON DELETE CASCADE |
| `title` | VARCHAR(500) | Название теста | NOT NULL |
| `questions_count` | INTEGER | Количество вопросов | DEFAULT 0 |
| `is_active` | BOOLEAN | Активен ли тест | DEFAULT true |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата обновления | DEFAULT NOW() ON UPDATE NOW() |

**Индексы:**
- `idx_tests_lesson` на `lesson_id`

---

### 14. `topics` - Темы уроков

Темы в рамках урока.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `lesson_id` | INTEGER | ID урока | FOREIGN KEY → lessons(id) ON DELETE CASCADE |
| `code` | VARCHAR(50) | Код темы (например, "Тема 1.1") | |
| `title` | VARCHAR(500) | Название темы | NOT NULL |
| `duration` | VARCHAR(50) | Продолжительность темы | |
| `order_index` | INTEGER | Порядок темы в уроке | NOT NULL, DEFAULT 0 |
| `is_active` | BOOLEAN | Активна ли тема | DEFAULT true |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата обновления | DEFAULT NOW() ON UPDATE NOW() |

**Индексы:**
- `idx_topics_lesson` на `lesson_id`
- `idx_topics_order` на `(lesson_id, order_index)`

---

### 15. `topic_files` - Файлы материалов тем

Файлы учебных материалов для тем (PDF, видео, документы).

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `topic_id` | INTEGER | ID темы | FOREIGN KEY → topics(id) ON DELETE CASCADE |
| `file_type` | ENUM('main_pdf', 'additional_video', 'additional_document') | Тип файла | NOT NULL |
| `original_name` | VARCHAR(500) | Оригинальное имя файла | NOT NULL |
| `file_size` | BIGINT | Размер файла в байтах | |
| `size_formatted` | VARCHAR(50) | Форматированный размер (например, "2.5 MB") | |
| `file_url` | VARCHAR(1000) | URL файла (presigned URL из MinIO) | |
| `minio_object_name` | VARCHAR(1000) | Имя объекта в MinIO | NOT NULL |
| `mime_type` | VARCHAR(100) | MIME тип файла | |
| `is_active` | BOOLEAN | Активен ли файл | DEFAULT true |
| `order_index` | INTEGER | Порядок отображения (для дополнительных файлов) | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата обновления | DEFAULT NOW() ON UPDATE NOW() |

**Индексы:**
- `idx_files_topic` на `topic_id`
- `idx_files_type` на `file_type`
- `idx_files_minio` на `minio_object_name`

**Ограничения:**
- Для каждой темы может быть только один файл с `file_type = 'main_pdf'`
- Дополнительные файлы имеют `file_type` = 'additional_video' или 'additional_document'

---

### 16. `final_tests` - Итоговые тесты

Итоговые тесты для программ курсов.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | INTEGER | Уникальный идентификатор | PRIMARY KEY, AUTO_INCREMENT |
| `course_program_id` | INTEGER | ID программы курса | FOREIGN KEY → course_programs(id) ON DELETE CASCADE |
| `title` | VARCHAR(500) | Название теста | NOT NULL |
| `questions_count` | INTEGER | Количество вопросов | DEFAULT 0 |
| `is_active` | BOOLEAN | Активен ли тест | DEFAULT true |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата обновления | DEFAULT NOW() ON UPDATE NOW() |

**Индексы:**
- `idx_final_tests_course` на `course_program_id`

---

## SQL скрипты создания таблиц

```sql
-- Таблица станций
CREATE TABLE stations (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    image VARCHAR(255),
    tech_map_image VARCHAR(500),
    power VARCHAR(100),
    commission_date VARCHAR(20),
    courses_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    location TEXT,
    type VARCHAR(255),
    design_capacity VARCHAR(100),
    gas_pressure VARCHAR(100),
    distance_from_border VARCHAR(100),
    pipeline_diameter VARCHAR(100),
    input_pressure VARCHAR(100),
    output_pressure VARCHAR(100),
    parallel_lines VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stations_short_name (short_name),
    INDEX idx_stations_status (status)
);

-- Источники поставки газа
CREATE TABLE station_gas_supply_sources (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    station_id INTEGER NOT NULL,
    source_name VARCHAR(255) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_gas_sources_station (station_id)
);

-- Оборудование станций
CREATE TABLE station_equipment (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    station_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    quantity INTEGER DEFAULT 1,
    power VARCHAR(100),
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_equipment_station (station_id)
);

-- Технические характеристики
CREATE TABLE station_specifications (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    station_id INTEGER NOT NULL,
    category VARCHAR(255) NOT NULL,
    value VARCHAR(100),
    unit VARCHAR(50),
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_specs_station (station_id)
);

-- Системы безопасности
CREATE TABLE station_safety_systems (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    station_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    manufacturer VARCHAR(255),
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_safety_station (station_id)
);

-- Особенности систем безопасности
CREATE TABLE station_safety_system_features (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    safety_system_id INTEGER NOT NULL,
    feature_name VARCHAR(255) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (safety_system_id) REFERENCES station_safety_systems(id) ON DELETE CASCADE,
    INDEX idx_features_safety (safety_system_id)
);

-- Программы курсов
CREATE TABLE course_programs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    station_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    duration VARCHAR(100),
    topics_count INTEGER DEFAULT 0,
    lessons_count INTEGER DEFAULT 0,
    tests_count INTEGER DEFAULT 0,
    format VARCHAR(50) DEFAULT 'Онлайн',
    is_active BOOLEAN DEFAULT TRUE,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_courses_station (station_id),
    INDEX idx_courses_active (is_active)
);

-- Результаты обучения
CREATE TABLE course_program_learning_outcomes (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course_program_id INTEGER NOT NULL,
    outcome_text TEXT NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_program_id) REFERENCES course_programs(id) ON DELETE CASCADE,
    INDEX idx_outcomes_course (course_program_id)
);

-- Требования к участникам
CREATE TABLE course_program_requirements (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course_program_id INTEGER NOT NULL,
    requirement_text TEXT NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_program_id) REFERENCES course_programs(id) ON DELETE CASCADE,
    INDEX idx_requirements_course (course_program_id)
);

-- Целевая аудитория
CREATE TABLE course_program_target_audience (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course_program_id INTEGER NOT NULL,
    audience_text VARCHAR(255) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_program_id) REFERENCES course_programs(id) ON DELETE CASCADE,
    INDEX idx_audience_course (course_program_id)
);

-- Уроки
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course_program_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    duration VARCHAR(100),
    topics_count INTEGER DEFAULT 0,
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_program_id) REFERENCES course_programs(id) ON DELETE CASCADE,
    INDEX idx_lessons_course (course_program_id),
    INDEX idx_lessons_order (course_program_id, order_index)
);

-- Материалы уроков
CREATE TABLE lesson_materials (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    lesson_id INTEGER NOT NULL,
    material_name VARCHAR(255) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    INDEX idx_materials_lesson (lesson_id)
);

-- Тесты уроков
CREATE TABLE lesson_tests (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    lesson_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    questions_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    INDEX idx_tests_lesson (lesson_id)
);

-- Темы
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    lesson_id INTEGER NOT NULL,
    code VARCHAR(50),
    title VARCHAR(500) NOT NULL,
    duration VARCHAR(50),
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    INDEX idx_topics_lesson (lesson_id),
    INDEX idx_topics_order (lesson_id, order_index)
);

-- Файлы материалов тем
CREATE TABLE topic_files (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    topic_id INTEGER NOT NULL,
    file_type ENUM('main_pdf', 'additional_video', 'additional_document') NOT NULL,
    original_name VARCHAR(500) NOT NULL,
    file_size BIGINT,
    size_formatted VARCHAR(50),
    file_url VARCHAR(1000),
    minio_object_name VARCHAR(1000) NOT NULL,
    mime_type VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    INDEX idx_files_topic (topic_id),
    INDEX idx_files_type (file_type),
    INDEX idx_files_minio (minio_object_name),
    UNIQUE KEY unique_main_pdf_per_topic (topic_id, file_type)
);

-- Итоговые тесты
CREATE TABLE final_tests (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course_program_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    questions_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_program_id) REFERENCES course_programs(id) ON DELETE CASCADE,
    INDEX idx_final_tests_course (course_program_id)
);
```

---

## Триггеры для автоматического подсчета

Для автоматического обновления счетчиков (`topics_count`, `lessons_count`, `tests_count`) можно использовать триггеры:

```sql
-- Триггер для обновления topics_count в lessons
DELIMITER //
CREATE TRIGGER update_lesson_topics_count
AFTER INSERT ON topics
FOR EACH ROW
BEGIN
    UPDATE lessons 
    SET topics_count = (SELECT COUNT(*) FROM topics WHERE lesson_id = NEW.lesson_id AND is_active = TRUE)
    WHERE id = NEW.lesson_id;
END//

CREATE TRIGGER update_lesson_topics_count_delete
AFTER DELETE ON topics
FOR EACH ROW
BEGIN
    UPDATE lessons 
    SET topics_count = (SELECT COUNT(*) FROM topics WHERE lesson_id = OLD.lesson_id AND is_active = TRUE)
    WHERE id = OLD.lesson_id;
END//

-- Триггер для обновления lessons_count в course_programs
CREATE TRIGGER update_course_lessons_count
AFTER INSERT ON lessons
FOR EACH ROW
BEGIN
    UPDATE course_programs 
    SET lessons_count = (SELECT COUNT(*) FROM lessons WHERE course_program_id = NEW.course_program_id AND is_active = TRUE)
    WHERE id = NEW.course_program_id;
END//

CREATE TRIGGER update_course_lessons_count_delete
AFTER DELETE ON lessons
FOR EACH ROW
BEGIN
    UPDATE course_programs 
    SET lessons_count = (SELECT COUNT(*) FROM lessons WHERE course_program_id = OLD.course_program_id AND is_active = TRUE)
    WHERE id = OLD.course_program_id;
END//

-- Триггер для обновления topics_count в course_programs (через lessons)
CREATE TRIGGER update_course_topics_count
AFTER INSERT ON topics
FOR EACH ROW
BEGIN
    DECLARE course_id INT;
    SELECT course_program_id INTO course_id FROM lessons WHERE id = NEW.lesson_id;
    UPDATE course_programs 
    SET topics_count = (
        SELECT COUNT(*) FROM topics 
        INNER JOIN lessons ON topics.lesson_id = lessons.id 
        WHERE lessons.course_program_id = course_id AND topics.is_active = TRUE
    )
    WHERE id = course_id;
END//
DELIMITER ;
```

---

## Основные операции для админ-панели

### 1. Управление станциями
- CRUD операции для таблицы `stations`
- Управление оборудованием (`station_equipment`)
- Управление техническими характеристиками (`station_specifications`)
- Управление системами безопасности (`station_safety_systems`)

### 2. Управление программами курсов
- CRUD операции для `course_programs`
- Управление результатами обучения (`course_program_learning_outcomes`)
- Управление требованиями (`course_program_requirements`)
- Управление целевой аудиторией (`course_program_target_audience`)

### 3. Управление уроками
- CRUD операции для `lessons`
- Управление материалами уроков (`lesson_materials`)
- Управление тестами уроков (`lesson_tests`)

### 4. Управление темами
- CRUD операции для `topics`
- Управление файлами материалов (`topic_files`)
- Загрузка файлов в MinIO и обновление записей в БД

### 5. Управление файлами
- Загрузка файлов в MinIO
- Создание presigned URLs для доступа
- Связывание файлов с темами
- Управление типами файлов (основной PDF / дополнительные материалы)

---

## Рекомендации по использованию

1. **Миграции данных**: Создайте систему миграций для постепенного переноса данных из `stationsData.js` в базу данных.

2. **Кэширование**: Используйте кэширование для часто запрашиваемых данных (списки станций, программы курсов).

3. **Валидация**: Реализуйте валидацию на уровне приложения и базы данных для обеспечения целостности данных.

4. **Аудит**: Рассмотрите возможность добавления таблиц аудита для отслеживания изменений в критических данных.

5. **Мягкое удаление**: Используйте поле `is_active` вместо физического удаления записей для возможности восстановления.

6. **Интеграция с MinIO**: Реализуйте автоматическую синхронизацию файлов между MinIO и базой данных при загрузке/удалении файлов.

---

## Примеры запросов

### Получение программы курса со всеми данными

```sql
SELECT 
    cp.*,
    s.name as station_name,
    s.short_name as station_short_name
FROM course_programs cp
JOIN stations s ON cp.station_id = s.id
WHERE cp.id = ? AND cp.is_active = TRUE;
```

### Получение уроков с темами

```sql
SELECT 
    l.*,
    COUNT(DISTINCT t.id) as actual_topics_count
FROM lessons l
LEFT JOIN topics t ON l.id = t.lesson_id AND t.is_active = TRUE
WHERE l.course_program_id = ? AND l.is_active = TRUE
GROUP BY l.id
ORDER BY l.order_index;
```

### Получение материалов темы

```sql
SELECT 
    tf.*,
    t.title as topic_title,
    t.code as topic_code
FROM topic_files tf
JOIN topics t ON tf.topic_id = t.id
WHERE tf.topic_id = ? AND tf.is_active = TRUE
ORDER BY 
    FIELD(tf.file_type, 'main_pdf', 'additional_video', 'additional_document'),
    tf.order_index;
```

---

## Заключение

Данная схема базы данных позволяет полноценно управлять всеми данными о станциях и их обучающих курсах через административную панель. Структура нормализована, индексирована и готова к использованию в production-окружении.






