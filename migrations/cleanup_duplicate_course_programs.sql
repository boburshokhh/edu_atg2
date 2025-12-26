-- Cleanup duplicate course_programs for station_id=1
-- Keep the most useful program: prefer one with lessons; then newest by updated_at/id.
-- Safe to run multiple times.

DO $$
DECLARE
  v_keep_id INTEGER;
BEGIN
  WITH candidates AS (
    SELECT
      cp.id,
      (SELECT COUNT(*) FROM course_program_lessons l WHERE l.course_program_id = cp.id) AS lessons_cnt,
      cp.updated_at
    FROM course_programs cp
    WHERE cp.station_id = 1
  )
  SELECT id INTO v_keep_id
  FROM candidates
  ORDER BY lessons_cnt DESC, updated_at DESC NULLS LAST, id DESC
  LIMIT 1;

  IF v_keep_id IS NULL THEN
    RAISE NOTICE 'No course_programs found for station_id=1';
    RETURN;
  END IF;

  -- Deactivate other programs
  UPDATE course_programs
  SET is_active = false
  WHERE station_id = 1 AND id <> v_keep_id;

  -- Delete empty duplicates (no lessons)
  DELETE FROM course_programs cp
  WHERE cp.station_id = 1
    AND cp.id <> v_keep_id
    AND NOT EXISTS (
      SELECT 1 FROM course_program_lessons l WHERE l.course_program_id = cp.id
    );

  RAISE NOTICE 'Kept program_id=% for station_id=1', v_keep_id;
END $$;


