-- Materials attached to Station training topics (course_program_topics).
-- Safe to run multiple times.

CREATE TABLE IF NOT EXISTS course_program_topic_files (
    id SERIAL PRIMARY KEY,
    course_program_topic_id INTEGER NOT NULL REFERENCES course_program_topics(id) ON DELETE CASCADE,
    title VARCHAR(500),
    original_name VARCHAR(500) NOT NULL,
    object_key VARCHAR(1000) NOT NULL,
    file_type VARCHAR(20) NOT NULL CHECK (file_type IN ('pdf', 'video', 'document')),
    is_main BOOLEAN NOT NULL DEFAULT false,
    order_index INTEGER NOT NULL DEFAULT 0,
    file_size BIGINT,
    mime_type VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cptf_topic_order
ON course_program_topic_files(course_program_topic_id, order_index);

CREATE INDEX IF NOT EXISTS idx_cptf_topic_main
ON course_program_topic_files(course_program_topic_id, is_main);

CREATE INDEX IF NOT EXISTS idx_cptf_object_key
ON course_program_topic_files(object_key);


