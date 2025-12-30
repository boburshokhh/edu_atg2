CREATE TABLE IF NOT EXISTS site_settings (
    id INTEGER PRIMARY KEY,
    hero_background_image VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO site_settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING;


