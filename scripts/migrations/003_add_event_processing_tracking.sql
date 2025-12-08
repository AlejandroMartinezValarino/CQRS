-- Migración: Tracking de eventos procesados para idempotencia
-- Descripción: Crea tabla para evitar procesar el mismo evento dos veces

CREATE TABLE IF NOT EXISTS processed_events (
    event_id VARCHAR(255) PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_duration_ms INTEGER,
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_processed_events_aggregate_id ON processed_events(aggregate_id);
CREATE INDEX IF NOT EXISTS idx_processed_events_type ON processed_events(event_type);
CREATE INDEX IF NOT EXISTS idx_processed_events_processed_at ON processed_events(processed_at DESC);