-- Migración: Crear Event Store
-- Descripción: Crea las tablas necesarias para el Event Store

CREATE TABLE IF NOT EXISTS event_store (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    occurred_at TIMESTAMP NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_event_store_aggregate_id ON event_store(aggregate_id);
CREATE INDEX IF NOT EXISTS idx_event_store_event_type ON event_store(event_type);
CREATE INDEX IF NOT EXISTS idx_event_store_occurred_at ON event_store(occurred_at);

