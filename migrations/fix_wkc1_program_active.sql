-- Проверка и исправление активности программы WKC-1
UPDATE course_programs 
SET is_active = true 
WHERE station_id = 1 AND title = 'Компрессорная станция WKC-1';

-- Проверка активности уроков
UPDATE course_program_lessons 
SET is_active = true 
WHERE course_program_id = (SELECT id FROM course_programs WHERE station_id = 1 AND title = 'Компрессорная станция WKC-1' LIMIT 1);

-- Проверка активности тем
UPDATE course_program_topics 
SET is_active = true 
WHERE course_program_lesson_id IN (
    SELECT id FROM course_program_lessons 
    WHERE course_program_id = (SELECT id FROM course_programs WHERE station_id = 1 AND title = 'Компрессорная станция WKC-1' LIMIT 1)
);

