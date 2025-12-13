"""Event Store en PostgreSQL con configuración para producción."""
import json
from datetime import datetime
from typing import List, Optional
import asyncpg
from asyncpg import Pool
from common.events.base_event import BaseEvent
from common.utils.logger import get_logger
from common.utils.retry import retry_async
from common.utils.db import get_pool_kwargs
from config.settings import settings

logger = get_logger(__name__)


class EventStore:
    """Implementación del Event Store usando PostgreSQL."""
    
    def __init__(self):
        self._pool: Optional[Pool] = None
        self._connected = False
    
    async def connect(self):
        """Crea el pool de conexiones con configuración para producción."""
        if self._pool and not self._pool.is_closing():
            logger.debug("Pool de conexiones ya existe")
            return
        
        try:
            logger.info(
                f"Conectando a Event Store: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
                f"{settings.POSTGRES_EVENT_STORE_DB}"
            )
            
            pool_kwargs = get_pool_kwargs(
                database=settings.POSTGRES_EVENT_STORE_DB,
                min_size=settings.POSTGRES_EVENT_STORE_MIN_CONNECTIONS,
                max_size=settings.POSTGRES_EVENT_STORE_MAX_CONNECTIONS,
                command_timeout=settings.POSTGRES_COMMAND_TIMEOUT,
            )
            # Agregar configuraciones adicionales
            pool_kwargs['connect_timeout'] = settings.POSTGRES_CONNECT_TIMEOUT
            pool_kwargs['max_queries'] = settings.POSTGRES_MAX_QUERIES
            pool_kwargs['max_inactive_connection_lifetime'] = settings.POSTGRES_MAX_INACTIVE_CONNECTION_LIFETIME
            pool_kwargs['server_settings'] = {
                'tcp_keepalives_idle': '600',
                'tcp_keepalives_interval': '30',
                'tcp_keepalives_count': '3',
            }
            self._pool = await asyncpg.create_pool(**pool_kwargs)
            self._connected = True
            logger.info("Conexión al Event Store establecida correctamente")
        except Exception as e:
            logger.error(f"Error conectando al Event Store: {e}", exc_info=True)
            self._connected = False
            raise
    
    async def close(self):
        """Cierra el pool de conexiones."""
        if self._pool:
            try:
                await self._pool.close()
                self._connected = False
                logger.info("Conexión al Event Store cerrada")
            except Exception as e:
                logger.error(f"Error cerrando pool del Event Store: {e}", exc_info=True)
    
    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def save_events(self, events: List[BaseEvent]):
        """Guarda eventos en el Event Store con retry."""
        if not self._pool or self._pool.is_closing():
            await self.connect()
        
        if not events:
            logger.warning("Intento de guardar lista vacía de eventos")
            return
        
        try:
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    for event in events:
                        await conn.execute("""
                            INSERT INTO event_store (
                                event_id, event_type, aggregate_id, event_data,
                                occurred_at, version, metadata
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ON CONFLICT (event_id) DO NOTHING
                        """, 
                            event.event_id,
                            event.event_type,
                            event.aggregate_id,
                            event.model_dump_json(),
                            event.occurred_at,
                            event.version,
                            json.dumps(event.metadata),
                        )
            
            logger.debug(f"Guardados {len(events)} eventos en Event Store")
        except Exception as e:
            logger.error(f"Error guardando eventos en Event Store: {e}", exc_info=True)
            raise
    
    async def health_check(self) -> bool:
        """Verifica la salud de la conexión al Event Store."""
        try:
            if not self._pool or self._pool.is_closing():
                return False
            
            async with self._pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Health check del Event Store falló: {e}")
            return False
    
    async def get_events_by_aggregate_id(
        self, 
        aggregate_id: str,
        from_version: int = 0
    ) -> List[BaseEvent]:
        """Obtiene eventos por aggregate_id."""
        if not self._pool:
            await self.connect()
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT event_data FROM event_store
                WHERE aggregate_id = $1 AND version > $2
                ORDER BY version ASC
            """, aggregate_id, from_version)
            
            events = []
            for row in rows:
                event_data = json.loads(row["event_data"])
                events.append(event_data)
            
            return events

