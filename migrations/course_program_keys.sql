-- Adds stable keys for lessons/topics so materials can be linked robustly.
-- Safe to run multiple times.

-- NOTE:
-- In this codebase, there is already a `lessons`/`topics` set of tables used for course content.
-- StationCourses program structure is stored separately in:
--   - course_programs
--   - course_program_lessons
--   - course_program_topics

-- =====================================================================
-- Station course program structure tables
-- =====================================================================

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

CREATE UNIQUE INDEX IF NOT EXISTS uq_course_program_lessons_lesson_key
ON course_program_lessons(lesson_key);

CREATE INDEX IF NOT EXISTS idx_course_program_lessons_program
ON course_program_lessons(course_program_id);

CREATE INDEX IF NOT EXISTS idx_course_program_lessons_order
ON course_program_lessons(course_program_id, order_index);

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

CREATE UNIQUE INDEX IF NOT EXISTS uq_course_program_topics_topic_key
ON course_program_topics(topic_key);

CREATE INDEX IF NOT EXISTS idx_course_program_topics_lesson
ON course_program_topics(course_program_lesson_id);

CREATE INDEX IF NOT EXISTS idx_course_program_topics_order
ON course_program_topics(course_program_lesson_id, order_index);

-- =====================================================================
-- Legacy safety: some environments may already have lesson_key/topic_key on lessons/topics.
-- Keep these for compatibility (no-op if already present).
-- =====================================================================

ALTER TABLE lessons
ADD COLUMN IF NOT EXISTS lesson_key TEXT;

ALTER TABLE topics
ADD COLUMN IF NOT EXISTS topic_key TEXT;

-- Uniqueness for non-null keys
CREATE UNIQUE INDEX IF NOT EXISTS uq_lessons_lesson_key
ON lessons(lesson_key)
WHERE lesson_key IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_topics_topic_key
ON topics(topic_key)
WHERE topic_key IS NOT NULL;


