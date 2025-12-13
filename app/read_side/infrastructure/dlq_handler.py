"""Manejador de Dead Letter Queue para eventos fallidos."""
from typing import Dict, Any, Optional
import asyncpg
import json
from datetime import datetime
from common.utils.logger import get_logger
from common.utils.db import get_pool_kwargs
from config.settings import settings

logger = get_logger(__name__)


class DLQHandler:
    """Maneja el almacenamiento de eventos fallidos en Dead Letter Queue."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Crea el pool de conexiones."""
        try:
            pool_kwargs = get_pool_kwargs(
                database=settings.POSTGRES_DB,
                min_size=1,
                max_size=5,
                command_timeout=settings.POSTGRES_COMMAND_TIMEOUT,
            )
            self._pool = await asyncpg.create_pool(**pool_kwargs)
            logger.info("Pool de conexiones del DLQHandler creado correctamente")
        except Exception as e:
            logger.error(f"Error creando pool de conexiones DLQ: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Cierra el pool."""
        if self._pool and not self._pool.is_closing():
            try:
                await self._pool.close()
                logger.info("Pool de conexiones del DLQHandler cerrado")
            except Exception as e:
                logger.error(f"Error cerrando pool DLQ: {e}", exc_info=True)
    
    async def store_failed_event(
        self,
        event: Dict[str, Any],
        error: Exception,
        kafka_topic: Optional[str] = None,
        kafka_partition: Optional[int] = None,
        kafka_offset: Optional[int] = None
    ) -> int:
        """
        Almacena un evento fallido en la DLQ.
        
        Returns:
            ID del registro en la DLQ
        """
        try:
            event_id = event.get("event_id", "unknown")
            event_type = event.get("event_type", "unknown")
            aggregate_id = event.get("aggregate_id")
            
            async with self._pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO dead_letter_queue (
                        event_id, event_type, aggregate_id, event_data,
                        error_type, error_message,
                        kafka_topic, kafka_partition, kafka_offset,
                        status
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING id
                """,
                    event_id,
                    event_type,
                    aggregate_id,
                    json.dumps(event),
                    type(error).__name__,
                    str(error),
                    kafka_topic,
                    kafka_partition,
                    kafka_offset,
                    'failed'
                )
                
                dlq_id = result["id"]
                logger.warning(
                    f"Evento fallido almacenado en DLQ: id={dlq_id}, "
                    f"event_id={event_id}, event_type={event_type}, "
                    f"error={type(error).__name__}: {str(error)}"
                )
                return dlq_id
                
        except Exception as e:
            logger.error(
                f"Error crítico almacenando evento en DLQ: {e}. "
                f"Evento original: {event.get('event_id', 'unknown')}",
                exc_info=True
            )
            raise
    
    async def get_failed_events(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Obtiene eventos fallidos de la DLQ.
        
        Args:
            status: Filtrar por status ('failed', 'retrying', 'resolved', 'archived')
            limit: Número máximo de eventos a retornar
        """
        async with self._pool.acquire() as conn:
            if status:
                rows = await conn.fetch("""
                    SELECT * FROM dead_letter_queue
                    WHERE status = $1
                    ORDER BY failed_at DESC
                    LIMIT $2
                """, status, limit)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM dead_letter_queue
                    ORDER BY failed_at DESC
                    LIMIT $1
                """, limit)
            
            return [dict(row) for row in rows]
    
    async def mark_for_retry(self, dlq_id: int) -> bool:
        """
        Marca un evento para reintento.
        
        Returns:
            True si se marcó correctamente, False si no existe
        """
        async with self._pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE dead_letter_queue
                SET status = 'retrying',
                    retry_count = retry_count + 1,
                    last_retry_at = CURRENT_TIMESTAMP
                WHERE id = $1 AND status = 'failed'
            """, dlq_id)
            
            return result == "UPDATE 1"
    
    async def mark_resolved(self, dlq_id: int, notes: Optional[str] = None) -> bool:
        """
        Marca un evento como resuelto.
        
        Returns:
            True si se marcó correctamente, False si no existe
        """
        async with self._pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE dead_letter_queue
                SET status = 'resolved',
                    resolved_at = CURRENT_TIMESTAMP,
                    notes = COALESCE($2, notes)
                WHERE id = $1
            """, dlq_id, notes)
            
            return result == "UPDATE 1"

