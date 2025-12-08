-- Migración: Dead Letter Queue (DLQ) para eventos fallidos
-- Descripción: Crea tabla para almacenar eventos que fallaron al procesarse

CREATE TABLE IF NOT EXISTS dead_letter_queue (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(255),
    event_data JSONB NOT NULL,
    error_type VARCHAR(255) NOT NULL,
    error_message TEXT NOT NULL,
    kafka_topic VARCHAR(255),
    kafka_partition INTEGER,
    kafka_offset BIGINT,
    failed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'failed', -- 'failed', 'retrying', 'resolved', 'archived'
    resolved_at TIMESTAMP,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_dlq_event_id ON dead_letter_queue(event_id);
CREATE INDEX IF NOT EXISTS idx_dlq_event_type ON dead_letter_queue(event_type);
CREATE INDEX IF NOT EXISTS idx_dlq_status ON dead_letter_queue(status);
CREATE INDEX IF NOT EXISTS idx_dlq_failed_at ON dead_letter_queue(failed_at DESC);
CREATE INDEX IF NOT EXISTS idx_dlq_retry_count ON dead_letter_queue(retry_count);

-- Comentarios para documentación
COMMENT ON TABLE dead_letter_queue IS 'Almacena eventos que fallaron al procesarse para revisión y reintento manual';
COMMENT ON COLUMN dead_letter_queue.status IS 'Estado del evento: failed (falló), retrying (reintentando), resolved (resuelto), archived (archivado)';

