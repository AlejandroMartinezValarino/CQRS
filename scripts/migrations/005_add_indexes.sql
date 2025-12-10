-- Índices para optimizar queries del read model

-- Índice para anime_stats ordenado por total_views (usado en top_animes_by_views)
CREATE INDEX IF NOT EXISTS idx_anime_stats_total_views 
ON anime_stats(total_views DESC);

-- Índice para anime_stats ordenado por average_rating (usado en top_animes_by_rating)
CREATE INDEX IF NOT EXISTS idx_anime_stats_average_rating 
ON anime_stats(average_rating DESC, total_ratings DESC);

-- Índice para anime_stats por anime_id (usado en get_anime_stats)
CREATE INDEX IF NOT EXISTS idx_anime_stats_anime_id 
ON anime_stats(anime_id);

-- Índice para animes por myanimelist_id (usado en get_anime)
CREATE INDEX IF NOT EXISTS idx_animes_myanimelist_id 
ON animes(myanimelist_id);

-- Índice compuesto para processed_events (usado en event_processor)
CREATE INDEX IF NOT EXISTS idx_processed_events_event_id_processed_at 
ON processed_events(event_id, processed_at);