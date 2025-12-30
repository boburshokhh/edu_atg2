CREATE TABLE IF NOT EXISTS hero_slider_images (
    id SERIAL PRIMARY KEY,
    key VARCHAR(500) NOT NULL,
    order_index INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hero_slider_order ON hero_slider_images(order_index, is_active);

