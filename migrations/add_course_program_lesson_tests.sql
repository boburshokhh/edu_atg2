-- ============================================================================
-- ДОБАВЛЕНИЕ ТАБЛИЦЫ ДЛЯ ТЕСТОВ К УРОКАМ ПРОГРАММЫ КУРСА
-- ============================================================================
-- Фронтенд ожидает lesson.test для каждого урока
-- ============================================================================

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

-- Комментарии
COMMENT ON TABLE course_program_lesson_tests IS 'Тесты к урокам программы курса (например: "Тестовые задания к Уроку 1")';
COMMENT ON COLUMN course_program_lesson_tests.course_program_lesson_id IS 'Ссылка на урок программы курса';
COMMENT ON COLUMN course_program_lesson_tests.questions_count IS 'Количество вопросов в тесте';

