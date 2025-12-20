-- Table to track background HLS transcode jobs
-- Idempotent / safe to re-run

CREATE TABLE IF NOT EXISTS video_transcode_jobs (
    id SERIAL PRIMARY KEY,
    target_type VARCHAR(50) NOT NULL,
    target_id INTEGER NOT NULL,
    station_id INTEGER NULL,
    source_object_key VARCHAR(1000) NOT NULL,
    master_object_key VARCHAR(1000) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    error TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_video_transcode_jobs_target ON video_transcode_jobs (target_type, target_id);


