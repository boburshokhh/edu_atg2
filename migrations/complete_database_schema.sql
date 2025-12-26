-- ============================================================================
-- ПОЛНАЯ МИГРАЦИЯ БАЗЫ ДАННЫХ ДЛЯ ПЛАТФОРМЫ ОБУЧЕНИЯ ATG EDUCATION
-- ============================================================================
-- Версия: 1.0
-- Дата: 2025-01-23
-- База данных: PostgreSQL (Supabase)
-- ============================================================================

-- ============================================================================
-- 1. ТАБЛИЦЫ АВТОРИЗАЦИИ И ПОЛЬЗОВАТЕЛЕЙ
-- ============================================================================

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
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

-- Комментарии к таблице users
COMMENT ON TABLE users IS 'Основная таблица пользователей системы';
COMMENT ON COLUMN users.role IS 'Роль пользователя: admin, user, instructor';
COMMENT ON COLUMN users.is_active IS 'Активен ли пользователь (может быть заблокирован)';

-- Индексы для users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Таблица сессий пользователей
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- Комментарии к таблице user_sessions
COMMENT ON TABLE user_sessions IS 'Сессии пользователей для управления авторизацией';
COMMENT ON COLUMN user_sessions.expires_at IS 'Время истечения сессии (обычно 24 часа)';

-- Индексы для user_sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Таблица расширенных профилей пользователей
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255),
    email VARCHAR(255),
    avatar_url TEXT,
    company VARCHAR(255),
    position VARCHAR(255),
    phone VARCHAR(50),
    bio TEXT,
    language VARCHAR(10) DEFAULT 'ru',
    email_notifications BOOLEAN DEFAULT true,
    push_notifications BOOLEAN DEFAULT true,
    weekly_report BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Комментарии к таблице user_profiles
COMMENT ON TABLE user_profiles IS 'Расширенные данные профиля пользователя';
COMMENT ON COLUMN user_profiles.avatar_url IS 'URL аватара (из Supabase Storage или base64)';
COMMENT ON COLUMN user_profiles.company IS 'Компания/станция пользователя';

-- Индексы для user_profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);

-- ============================================================================
-- 2. ТАБЛИЦЫ СТАНЦИЙ
-- ============================================================================

-- Таблица станций
CREATE TABLE IF NOT EXISTS stations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    image VARCHAR(255),
    tech_map_image VARCHAR(500),
    power VARCHAR(100),
    commission_date VARCHAR(20),
    courses_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'maintenance')),
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к таблице stations
COMMENT ON TABLE stations IS 'Компрессорные станции компании';
COMMENT ON COLUMN stations.short_name IS 'Краткое название станции (WKC1, WKC2, UCS1 и т.д.)';
COMMENT ON COLUMN stations.courses_count IS 'Количество курсов для станции (вычисляемое поле)';

-- Индексы для stations
CREATE INDEX IF NOT EXISTS idx_stations_short_name ON stations(short_name);
CREATE INDEX IF NOT EXISTS idx_stations_status ON stations(status);

-- Таблица источников поставки газа
CREATE TABLE IF NOT EXISTS station_gas_supply_sources (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    source_name VARCHAR(255) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для station_gas_supply_sources
CREATE INDEX IF NOT EXISTS idx_gas_sources_station ON station_gas_supply_sources(station_id);

-- Таблица оборудования станций
CREATE TABLE IF NOT EXISTS station_equipment (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    quantity INTEGER DEFAULT 1,
    power VARCHAR(100),
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для station_equipment
CREATE INDEX IF NOT EXISTS idx_equipment_station ON station_equipment(station_id);

-- Таблица технических характеристик
CREATE TABLE IF NOT EXISTS station_specifications (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    category VARCHAR(255) NOT NULL,
    value VARCHAR(100),
    unit VARCHAR(50),
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для station_specifications
CREATE INDEX IF NOT EXISTS idx_specs_station ON station_specifications(station_id);

-- Таблица систем безопасности
CREATE TABLE IF NOT EXISTS station_safety_systems (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    manufacturer VARCHAR(255),
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для station_safety_systems
CREATE INDEX IF NOT EXISTS idx_safety_station ON station_safety_systems(station_id);

-- Таблица особенностей систем безопасности
CREATE TABLE IF NOT EXISTS station_safety_system_features (
    id SERIAL PRIMARY KEY,
    safety_system_id INTEGER NOT NULL REFERENCES station_safety_systems(id) ON DELETE CASCADE,
    feature_name VARCHAR(255) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для station_safety_system_features
CREATE INDEX IF NOT EXISTS idx_features_safety ON station_safety_system_features(safety_system_id);

-- Таблица фотографий станций
CREATE TABLE IF NOT EXISTS station_photos (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    view VARCHAR(100),
    image_url VARCHAR(500) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для station_photos
CREATE INDEX IF NOT EXISTS idx_photos_station ON station_photos(station_id);
CREATE INDEX IF NOT EXISTS idx_photos_order ON station_photos(station_id, order_index);

-- Таблица нормативных документов станций
CREATE TABLE IF NOT EXISTS station_normative_docs (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для station_normative_docs
CREATE INDEX IF NOT EXISTS idx_normative_docs_station ON station_normative_docs(station_id);

-- Таблица промо-видео станций
CREATE TABLE IF NOT EXISTS station_promo_videos (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    title VARCHAR(255),
    object_key VARCHAR(1000) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для station_promo_videos
CREATE INDEX IF NOT EXISTS idx_promo_videos_station ON station_promo_videos(station_id);
CREATE INDEX IF NOT EXISTS idx_promo_videos_active ON station_promo_videos(station_id, is_active);

-- ============================================================================
-- 3. ТАБЛИЦЫ КУРСОВ И ПРОГРАММ ОБУЧЕНИЯ
-- ============================================================================

-- Таблица программ курсов
CREATE TABLE IF NOT EXISTS course_programs (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    duration VARCHAR(100),
    topics_count INTEGER DEFAULT 0,
    lessons_count INTEGER DEFAULT 0,
    tests_count INTEGER DEFAULT 0,
    format VARCHAR(50) DEFAULT 'Онлайн',
    is_active BOOLEAN DEFAULT true,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к таблице course_programs
COMMENT ON TABLE course_programs IS 'Программы обучения для станций';
COMMENT ON COLUMN course_programs.topics_count IS 'Количество тем (вычисляемое поле)';
COMMENT ON COLUMN course_programs.lessons_count IS 'Количество уроков (вычисляемое поле)';
COMMENT ON COLUMN course_programs.tests_count IS 'Количество тестов (вычисляемое поле)';

-- Индексы для course_programs
CREATE INDEX IF NOT EXISTS idx_courses_station ON course_programs(station_id);
CREATE INDEX IF NOT EXISTS idx_courses_active ON course_programs(is_active);

-- Таблица результатов обучения
CREATE TABLE IF NOT EXISTS course_program_learning_outcomes (
    id SERIAL PRIMARY KEY,
    course_program_id INTEGER NOT NULL REFERENCES course_programs(id) ON DELETE CASCADE,
    outcome_text TEXT NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для course_program_learning_outcomes
CREATE INDEX IF NOT EXISTS idx_outcomes_course ON course_program_learning_outcomes(course_program_id);

-- Таблица требований к участникам
CREATE TABLE IF NOT EXISTS course_program_requirements (
    id SERIAL PRIMARY KEY,
    course_program_id INTEGER NOT NULL REFERENCES course_programs(id) ON DELETE CASCADE,
    requirement_text TEXT NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для course_program_requirements
CREATE INDEX IF NOT EXISTS idx_requirements_course ON course_program_requirements(course_program_id);

-- Таблица целевой аудитории
CREATE TABLE IF NOT EXISTS course_program_target_audience (
    id SERIAL PRIMARY KEY,
    course_program_id INTEGER NOT NULL REFERENCES course_programs(id) ON DELETE CASCADE,
    audience_text VARCHAR(255) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для course_program_target_audience
CREATE INDEX IF NOT EXISTS idx_audience_course ON course_program_target_audience(course_program_id);

-- Таблица уроков программы курса (для структуры программы станции)
CREATE TABLE IF NOT EXISTS course_program_lessons (
    id SERIAL PRIMARY KEY,
    course_program_id INTEGER NOT NULL REFERENCES course_programs(id) ON DELETE CASCADE,
    lesson_key TEXT NOT NULL,
    title VARCHAR(500) NOT NULL,
    duration VARCHAR(100),
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для course_program_lessons
CREATE UNIQUE INDEX IF NOT EXISTS uq_course_program_lessons_lesson_key
ON course_program_lessons(lesson_key);
CREATE INDEX IF NOT EXISTS idx_course_program_lessons_program
ON course_program_lessons(course_program_id);
CREATE INDEX IF NOT EXISTS idx_course_program_lessons_order
ON course_program_lessons(course_program_id, order_index);

-- Таблица тем программы курса (для структуры программы станции)
CREATE TABLE IF NOT EXISTS course_program_topics (
    id SERIAL PRIMARY KEY,
    course_program_lesson_id INTEGER NOT NULL REFERENCES course_program_lessons(id) ON DELETE CASCADE,
    topic_key TEXT NOT NULL,
    code VARCHAR(50),
    title VARCHAR(500) NOT NULL,
    duration VARCHAR(50),
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для course_program_topics
CREATE UNIQUE INDEX IF NOT EXISTS uq_course_program_topics_topic_key
ON course_program_topics(topic_key);
CREATE INDEX IF NOT EXISTS idx_course_program_topics_lesson
ON course_program_topics(course_program_lesson_id);
CREATE INDEX IF NOT EXISTS idx_course_program_topics_order
ON course_program_topics(course_program_lesson_id, order_index);

-- Таблица тестов к урокам программы курса
CREATE TABLE IF NOT EXISTS course_program_lesson_tests (
    id SERIAL PRIMARY KEY,
    course_program_lesson_id INTEGER NOT NULL REFERENCES course_program_lessons(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    questions_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для course_program_lesson_tests
CREATE INDEX IF NOT EXISTS idx_lesson_tests_lesson 
ON course_program_lesson_tests(course_program_lesson_id);
CREATE INDEX IF NOT EXISTS idx_lesson_tests_active 
ON course_program_lesson_tests(course_program_lesson_id, is_active);

-- Комментарии для course_program_lesson_tests
COMMENT ON TABLE course_program_lesson_tests IS 'Тесты к урокам программы курса (например: "Тестовые задания к Уроку 1")';
COMMENT ON COLUMN course_program_lesson_tests.questions_count IS 'Количество вопросов в тесте';

-- ============================================================================
-- 4. ТАБЛИЦЫ УРОКОВ И ТЕМ
-- ============================================================================

-- Таблица уроков
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    course_program_id INTEGER NOT NULL REFERENCES course_programs(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    duration VARCHAR(100),
    topics_count INTEGER DEFAULT 0,
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к таблице lessons
COMMENT ON TABLE lessons IS 'Уроки в рамках программы курса';
COMMENT ON COLUMN lessons.topics_count IS 'Количество тем в уроке (вычисляемое поле)';

-- Индексы для lessons
CREATE INDEX IF NOT EXISTS idx_lessons_course ON lessons(course_program_id);
CREATE INDEX IF NOT EXISTS idx_lessons_order ON lessons(course_program_id, order_index);

-- Таблица материалов уроков
CREATE TABLE IF NOT EXISTS lesson_materials (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    material_name VARCHAR(255) NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для lesson_materials
CREATE INDEX IF NOT EXISTS idx_materials_lesson ON lesson_materials(lesson_id);

-- Таблица тестов уроков
CREATE TABLE IF NOT EXISTS lesson_tests (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    questions_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для lesson_tests
CREATE INDEX IF NOT EXISTS idx_tests_lesson ON lesson_tests(lesson_id);

-- Таблица тем
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    code VARCHAR(50),
    title VARCHAR(500) NOT NULL,
    duration VARCHAR(50),
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к таблице topics
COMMENT ON TABLE topics IS 'Темы в рамках урока';
COMMENT ON COLUMN topics.code IS 'Код темы (например, "Тема 1.1")';

-- Индексы для topics
CREATE INDEX IF NOT EXISTS idx_topics_lesson ON topics(lesson_id);
CREATE INDEX IF NOT EXISTS idx_topics_order ON topics(lesson_id, order_index);

-- Таблица файлов материалов тем
CREATE TABLE IF NOT EXISTS topic_files (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    file_type VARCHAR(50) NOT NULL CHECK (file_type IN ('main_pdf', 'additional_video', 'additional_document')),
    original_name VARCHAR(500) NOT NULL,
    file_size BIGINT,
    size_formatted VARCHAR(50),
    file_url VARCHAR(1000),
    minio_object_name VARCHAR(1000) NOT NULL,
    mime_type VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_main_pdf_per_topic UNIQUE (topic_id, file_type) DEFERRABLE INITIALLY DEFERRED
);

-- Комментарии к таблице topic_files
COMMENT ON TABLE topic_files IS 'Файлы учебных материалов для тем (PDF, видео, документы)';
COMMENT ON COLUMN topic_files.file_type IS 'Тип файла: main_pdf (основной PDF), additional_video, additional_document';
COMMENT ON COLUMN topic_files.minio_object_name IS 'Путь к файлу в MinIO хранилище';

-- Индексы для topic_files
CREATE INDEX IF NOT EXISTS idx_files_topic ON topic_files(topic_id);
CREATE INDEX IF NOT EXISTS idx_files_type ON topic_files(file_type);
CREATE INDEX IF NOT EXISTS idx_files_minio ON topic_files(minio_object_name);

-- Таблица итоговых тестов
CREATE TABLE IF NOT EXISTS final_tests (
    id SERIAL PRIMARY KEY,
    course_program_id INTEGER NOT NULL REFERENCES course_programs(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    questions_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для final_tests
CREATE INDEX IF NOT EXISTS idx_final_tests_course ON final_tests(course_program_id);

-- ============================================================================
-- 5. ТАБЛИЦЫ ПОЛЬЗОВАТЕЛЬСКИХ КУРСОВ И ПРОГРЕССА
-- ============================================================================

-- Таблица курсов (для пользовательских курсов)
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    station_id INTEGER REFERENCES stations(id) ON DELETE SET NULL,
    duration_hours INTEGER,
    level VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    icon VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для courses
CREATE INDEX IF NOT EXISTS idx_courses_station_id ON courses(station_id);
CREATE INDEX IF NOT EXISTS idx_courses_is_active ON courses(is_active);

-- Таблица участия пользователей в курсах
CREATE TABLE IF NOT EXISTS user_courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    progress_percent INTEGER DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
    status VARCHAR(20) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    hours_studied NUMERIC(10, 2) DEFAULT 0,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, course_id)
);

-- Комментарии к таблице user_courses
COMMENT ON TABLE user_courses IS 'Участие пользователей в курсах с отслеживанием прогресса';
COMMENT ON COLUMN user_courses.progress_percent IS 'Процент выполнения курса (0-100)';
COMMENT ON COLUMN user_courses.status IS 'Статус прохождения: not_started, in_progress, completed';

-- Индексы для user_courses
CREATE INDEX IF NOT EXISTS idx_user_courses_user_id ON user_courses(user_id);
CREATE INDEX IF NOT EXISTS idx_user_courses_course_id ON user_courses(course_id);
CREATE INDEX IF NOT EXISTS idx_user_courses_status ON user_courses(status);
CREATE INDEX IF NOT EXISTS idx_user_courses_last_activity ON user_courses(last_activity DESC);

-- Таблица сертификатов
CREATE TABLE IF NOT EXISTS certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pdf_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для certificates
CREATE INDEX IF NOT EXISTS idx_certificates_user_id ON certificates(user_id);
CREATE INDEX IF NOT EXISTS idx_certificates_course_id ON certificates(course_id);
CREATE INDEX IF NOT EXISTS idx_certificates_issued_at ON certificates(issued_at DESC);

-- Таблица статистики пользователей
CREATE TABLE IF NOT EXISTS user_stats (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    active_courses INTEGER DEFAULT 0,
    completed_courses INTEGER DEFAULT 0,
    total_hours_studied NUMERIC(10, 2) DEFAULT 0,
    certificates_count INTEGER DEFAULT 0,
    achievements JSONB DEFAULT '{}'::jsonb,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Комментарии к таблице user_stats
COMMENT ON TABLE user_stats IS 'Статистика пользователей (вычисляемые поля)';
COMMENT ON COLUMN user_stats.achievements IS 'Достижения пользователя в формате JSON';

-- ============================================================================
-- 6. ФУНКЦИИ БАЗЫ ДАННЫХ
-- ============================================================================

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Функция для очистки истекших сессий
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Функция для обновления счетчика курсов станции
CREATE OR REPLACE FUNCTION update_station_courses_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE stations
        SET courses_count = (
            SELECT COUNT(*) 
            FROM course_programs 
            WHERE station_id = NEW.station_id AND is_active = true
        )
        WHERE id = NEW.station_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE stations
        SET courses_count = (
            SELECT COUNT(*) 
            FROM course_programs 
            WHERE station_id = OLD.station_id AND is_active = true
        )
        WHERE id = OLD.station_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Функция для обновления счетчика уроков в программе курса
CREATE OR REPLACE FUNCTION update_course_lessons_count()
RETURNS TRIGGER AS $$
DECLARE
    course_id INTEGER;
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        course_id := NEW.course_program_id;
    ELSE
        course_id := OLD.course_program_id;
    END IF;
    
    UPDATE course_programs
    SET lessons_count = (
        SELECT COUNT(*) 
        FROM lessons 
        WHERE course_program_id = course_id AND is_active = true
    )
    WHERE id = course_id;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Функция для обновления счетчика тем в уроке
CREATE OR REPLACE FUNCTION update_lesson_topics_count()
RETURNS TRIGGER AS $$
DECLARE
    lesson_id INTEGER;
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        lesson_id := NEW.lesson_id;
    ELSE
        lesson_id := OLD.lesson_id;
    END IF;
    
    UPDATE lessons
    SET topics_count = (
        SELECT COUNT(*) 
        FROM topics 
        WHERE lesson_id = lesson_id AND is_active = true
    )
    WHERE id = lesson_id;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Функция для обновления счетчика тем в программе курса
CREATE OR REPLACE FUNCTION update_course_topics_count()
RETURNS TRIGGER AS $$
DECLARE
    course_id INTEGER;
BEGIN
    -- Получаем course_program_id через lesson_id
    SELECT course_program_id INTO course_id
    FROM lessons
    WHERE id = (
        CASE 
            WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN NEW.lesson_id
            ELSE OLD.lesson_id
        END
    );
    
    IF course_id IS NOT NULL THEN
        UPDATE course_programs
        SET topics_count = (
            SELECT COUNT(*) 
            FROM topics 
            INNER JOIN lessons ON topics.lesson_id = lessons.id 
            WHERE lessons.course_program_id = course_id AND topics.is_active = true
        )
        WHERE id = course_id;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. ТРИГГЕРЫ
-- ============================================================================

-- Триггер для автоматического обновления updated_at в users
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Триггер для автоматического обновления updated_at в user_profiles
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Триггер для обновления счетчика курсов станции
DROP TRIGGER IF EXISTS trigger_update_station_courses_count ON course_programs;
CREATE TRIGGER trigger_update_station_courses_count
    AFTER INSERT OR UPDATE OR DELETE ON course_programs
    FOR EACH ROW
    EXECUTE FUNCTION update_station_courses_count();

-- Триггер для обновления счетчика уроков в программе курса
DROP TRIGGER IF EXISTS trigger_update_course_lessons_count_insert ON lessons;
CREATE TRIGGER trigger_update_course_lessons_count_insert
    AFTER INSERT OR UPDATE ON lessons
    FOR EACH ROW
    EXECUTE FUNCTION update_course_lessons_count();

DROP TRIGGER IF EXISTS trigger_update_course_lessons_count_delete ON lessons;
CREATE TRIGGER trigger_update_course_lessons_count_delete
    AFTER DELETE ON lessons
    FOR EACH ROW
    EXECUTE FUNCTION update_course_lessons_count();

-- Триггер для обновления счетчика тем в уроке
DROP TRIGGER IF EXISTS trigger_update_lesson_topics_count_insert ON topics;
CREATE TRIGGER trigger_update_lesson_topics_count_insert
    AFTER INSERT OR UPDATE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION update_lesson_topics_count();

DROP TRIGGER IF EXISTS trigger_update_lesson_topics_count_delete ON topics;
CREATE TRIGGER trigger_update_lesson_topics_count_delete
    AFTER DELETE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION update_lesson_topics_count();

-- Триггер для обновления счетчика тем в программе курса
DROP TRIGGER IF EXISTS trigger_update_course_topics_count ON topics;
CREATE TRIGGER trigger_update_course_topics_count
    AFTER INSERT OR UPDATE OR DELETE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION update_course_topics_count();

-- ============================================================================
-- 8. ROW LEVEL SECURITY (RLS) ПОЛИТИКИ
-- ============================================================================
-- ПРИМЕЧАНИЕ: RLS отключен, так как авторизация управляется Django backend
-- Если нужно включить RLS, создайте политики без использования auth.uid()
-- (который доступен только в Supabase)

-- ============================================================================
-- 9. ИНИЦИАЛИЗАЦИЯ ДАННЫХ (ОПЦИОНАЛЬНО)
-- ============================================================================

-- Создание тестового администратора (пароль: password123)
-- ВНИМАНИЕ: В продакшене используйте хеширование паролей!
INSERT INTO users (username, password_hash, full_name, email, role, is_active)
VALUES ('admin', 'password123', 'Администратор системы', 'admin@atg.uz', 'admin', true)
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- 10. КОММЕНТАРИИ И ДОКУМЕНТАЦИЯ
-- ============================================================================

COMMENT ON SCHEMA public IS 'Схема базы данных для платформы обучения ATG Education';

-- ============================================================================
-- КОНЕЦ МИГРАЦИИ
-- ============================================================================

-- Для проверки успешного выполнения миграции выполните:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

