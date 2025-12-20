-- Station promo videos (short video about station).
-- Safe to run multiple times.

CREATE TABLE IF NOT EXISTS station_promo_videos (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    title VARCHAR(255),
    object_key VARCHAR(1000) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- One active promo video per station
CREATE UNIQUE INDEX IF NOT EXISTS uq_station_promo_video_active
ON station_promo_videos(station_id)
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_station_promo_video_station
ON station_promo_videos(station_id);


