-- ============================================================================
-- User course program enrollments and materials progress
-- ============================================================================

-- Table: user_course_programs
CREATE TABLE IF NOT EXISTS user_course_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_program_id INTEGER NOT NULL REFERENCES course_programs(id) ON DELETE CASCADE,
    progress_percent INTEGER DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
    status VARCHAR(20) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    hours_studied NUMERIC(10, 2) DEFAULT 0,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, course_program_id)
);

COMMENT ON TABLE user_course_programs IS 'User enrollments for course programs with progress tracking';
COMMENT ON COLUMN user_course_programs.progress_percent IS 'Completion percent (0-100)';
COMMENT ON COLUMN user_course_programs.status IS 'Status: not_started, in_progress, completed';

CREATE INDEX IF NOT EXISTS idx_user_course_programs_user ON user_course_programs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_course_programs_program ON user_course_programs(course_program_id);
CREATE INDEX IF NOT EXISTS idx_user_course_programs_status ON user_course_programs(status);
CREATE INDEX IF NOT EXISTS idx_user_course_programs_last_activity ON user_course_programs(last_activity DESC);

-- Table: user_course_materials
CREATE TABLE IF NOT EXISTS user_course_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_program_id INTEGER NOT NULL REFERENCES course_programs(id) ON DELETE CASCADE,
    material_type VARCHAR(20) NOT NULL CHECK (material_type IN ('video', 'pdf', 'text', 'presentation', 'test')),
    material_key TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT false,
    viewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, course_program_id, material_type, material_key)
);

COMMENT ON TABLE user_course_materials IS 'Per-material progress for course programs';
COMMENT ON COLUMN user_course_materials.material_key IS 'Lesson/topic/file key for identifying a material';

CREATE INDEX IF NOT EXISTS idx_user_course_materials_user_program ON user_course_materials(user_id, course_program_id);
CREATE INDEX IF NOT EXISTS idx_user_course_materials_completed ON user_course_materials(is_completed);
