-- ============================================================================
-- ДОБАВЛЕНИЕ НЕДОСТАЮЩИХ ТАБЛИЦ ДЛЯ СТАНЦИЙ
-- ============================================================================
-- Добавляет таблицы: station_photos, station_normative_docs, station_promo_videos
-- ============================================================================

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

-- Комментарии для station_photos
COMMENT ON TABLE station_photos IS 'Фотографии станций';
COMMENT ON COLUMN station_photos.view IS 'Вид/тип фотографии (например: общий вид, оборудование и т.д.)';
COMMENT ON COLUMN station_photos.order_index IS 'Порядок отображения фотографий';

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

-- Комментарии для station_normative_docs
COMMENT ON TABLE station_normative_docs IS 'Нормативные документы для станций';
COMMENT ON COLUMN station_normative_docs.file_url IS 'URL файла документа (хранится в MinIO или другом хранилище)';

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

-- Комментарии для station_promo_videos
COMMENT ON TABLE station_promo_videos IS 'Промо-видео для станций';
COMMENT ON COLUMN station_promo_videos.object_key IS 'Ключ объекта в MinIO или другом хранилище';
COMMENT ON COLUMN station_promo_videos.is_active IS 'Активно ли видео для отображения';

