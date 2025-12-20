-- Fix session_token column to support longer JWT tokens
-- JWT tokens can be longer than 255 characters, so we need to change from VARCHAR(255) to TEXT

-- Check if column exists and is VARCHAR(255), then alter it
DO $$
BEGIN
    -- Check if the column is VARCHAR(255) and change to TEXT
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'user_sessions' 
        AND column_name = 'session_token'
        AND character_maximum_length = 255
    ) THEN
        ALTER TABLE user_sessions 
        ALTER COLUMN session_token TYPE TEXT;
        
        RAISE NOTICE 'Changed session_token column from VARCHAR(255) to TEXT';
    ELSE
        RAISE NOTICE 'session_token column does not exist or is already TEXT';
    END IF;
END $$;

