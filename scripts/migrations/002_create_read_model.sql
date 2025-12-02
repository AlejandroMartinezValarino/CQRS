-- Migración: Crear Read Model
-- Descripción: Crea las tablas para las proyecciones del read model

-- Tabla de estadísticas de clicks
CREATE TABLE IF NOT EXISTS anime_clicks (
    anime_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    click_count INTEGER DEFAULT 1,
    last_click_at TIMESTAMP NOT NULL,
    PRIMARY KEY (anime_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_anime_clicks_anime_id ON anime_clicks(anime_id);
CREATE INDEX IF NOT EXISTS idx_anime_clicks_count ON anime_clicks(click_count DESC);

-- Tabla de estadísticas de visualizaciones
CREATE TABLE IF NOT EXISTS anime_views (
    anime_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    view_count INTEGER DEFAULT 1,
    total_duration_seconds INTEGER DEFAULT 0,
    last_view_at TIMESTAMP NOT NULL,
    PRIMARY KEY (anime_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_anime_views_anime_id ON anime_views(anime_id);
CREATE INDEX IF NOT EXISTS idx_anime_views_count ON anime_views(view_count DESC);

-- Tabla de calificaciones
CREATE TABLE IF NOT EXISTS anime_ratings (
    anime_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    rating NUMERIC(3, 2) NOT NULL CHECK (rating >= 0 AND rating <= 10),
    rated_at TIMESTAMP NOT NULL,
    PRIMARY KEY (anime_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_anime_ratings_anime_id ON anime_ratings(anime_id);
CREATE INDEX IF NOT EXISTS idx_anime_ratings_rating ON anime_ratings(rating DESC);

-- Tabla agregada de estadísticas por anime
CREATE TABLE IF NOT EXISTS anime_stats (
    anime_id INTEGER PRIMARY KEY,
    total_clicks INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_ratings INTEGER DEFAULT 0,
    average_rating NUMERIC(5, 2) DEFAULT 0,
    total_duration_seconds INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anime_stats_clicks ON anime_stats(total_clicks DESC);
CREATE INDEX IF NOT EXISTS idx_anime_stats_views ON anime_stats(total_views DESC);
CREATE INDEX IF NOT EXISTS idx_anime_stats_rating ON anime_stats(average_rating DESC);

