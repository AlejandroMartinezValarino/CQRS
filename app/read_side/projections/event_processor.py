from typing import Dict, Any, Optional
import asyncpg
import time
from datetime import datetime
from common.events.anime_events import ClickRegistered, ViewRegistered, RatingGiven
from common.utils.logger import get_logger
from common.utils.retry import retry_async
from common.exceptions import DomainException
from config.settings import settings

logger = get_logger(__name__)


class EventProcessingError(DomainException):
    """Excepción lanzada cuando falla el procesamiento de un evento."""
    pass


class EventProcessor:
    """Procesa eventos y actualiza las proyecciones con idempotencia y logging."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Crea el pool de conexiones."""
        try:
            self._pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=2,
                max_size=10,
            )
            logger.info("Pool de conexiones del EventProcessor creado correctamente")
        except Exception as e:
            logger.error(f"Error creando pool de conexiones: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Cierra el pool."""
        if self._pool:
            try:
                await self._pool.close()
                logger.info("Pool de conexiones del EventProcessor cerrado")
            except Exception as e:
                logger.error(f"Error cerrando pool: {e}", exc_info=True)
    
    async def _is_event_processed(self, event_id: str) -> bool:
        """Verifica si un evento ya fue procesado (idempotencia)."""
        async with self._pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM processed_events WHERE event_id = $1 AND status = 'success')",
                event_id
            )
            return result
    
    async def _mark_event_processed(
        self, 
        event_id: str, 
        event_type: str, 
        aggregate_id: str,
        duration_ms: int,
        status: str = 'success',
        error_message: Optional[str] = None
    ):
        """Marca un evento como procesado."""
        async with self._pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO processed_events 
                (event_id, event_type, aggregate_id, processing_duration_ms, status, error_message)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (event_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    error_message = EXCLUDED.error_message,
                    processing_duration_ms = EXCLUDED.processing_duration_ms,
                    processed_at = CURRENT_TIMESTAMP
            """, event_id, event_type, aggregate_id, duration_ms, status, error_message)
    
    def _validate_event(self, event: Dict[str, Any], required_fields: list) -> None:
        """Valida que un evento tenga los campos requeridos."""
        missing_fields = [field for field in required_fields if field not in event]
        if missing_fields:
            raise EventProcessingError(
                f"Evento inválido: faltan campos requeridos: {missing_fields}"
            )
    
    def _parse_ts(self, value: Any) -> datetime:
        """Convierte strings ISO a datetime para inserción en DB."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                if value.endswith("Z"):
                    value = value.replace("Z", "+00:00")
                return datetime.fromisoformat(value)
            except Exception as e:
                raise EventProcessingError(f"Timestamp inválido: {value}") from e
        raise EventProcessingError(f"Timestamp inválido: {value}")
    
    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def process_click_event(self, event: Dict[str, Any]):
        """Procesa un evento de click con validación e idempotencia."""
        start_time = time.time()
        event_id = event.get("event_id")
        event_type = event.get("event_type", "ClickRegistered")
        aggregate_id = event.get("aggregate_id")
        
        self._validate_event(event, ["anime_id", "user_id", "occurred_at", "event_id"])
        
        if await self._is_event_processed(event_id):
            logger.info(f"Evento {event_id} ya fue procesado, saltando (idempotencia)")
            return
        
        try:
            anime_id = event["anime_id"]
            user_id = event["user_id"]
            occurred_at = self._parse_ts(event["occurred_at"])
            
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("""
                        INSERT INTO anime_clicks (anime_id, user_id, last_click_at)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (anime_id, user_id) DO UPDATE SET
                            click_count = anime_clicks.click_count + 1,
                            last_click_at = EXCLUDED.last_click_at
                    """, anime_id, user_id, occurred_at)
                    
                    await conn.execute("""
                        INSERT INTO anime_stats (anime_id, total_clicks)
                        VALUES ($1, 1)
                        ON CONFLICT (anime_id) DO UPDATE SET
                            total_clicks = anime_stats.total_clicks + 1,
                            updated_at = CURRENT_TIMESTAMP
                    """, anime_id)
            
            duration_ms = int((time.time() - start_time) * 1000)
            await self._mark_event_processed(
                event_id, event_type, aggregate_id, duration_ms, 'success'
            )
            logger.info(
                f"Evento ClickRegistered procesado: anime_id={anime_id}, user_id={user_id}, "
                f"duration={duration_ms}ms"
            )

            if hasattr(self, '_repository') and self._repository:
                self._repository.invalidate_anime_cache(anime_id)
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            await self._mark_event_processed(
                event_id, event_type, aggregate_id, duration_ms, 'error', error_msg
            )
            logger.error(
                f"Error procesando evento ClickRegistered {event_id}: {e}",
                exc_info=True
            )
            raise EventProcessingError(f"Error procesando evento de click: {e}") from e
    
    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def process_view_event(self, event: Dict[str, Any]):
        """Procesa un evento de visualización con validación e idempotencia."""
        start_time = time.time()
        event_id = event.get("event_id")
        event_type = event.get("event_type", "ViewRegistered")
        aggregate_id = event.get("aggregate_id")
        
        self._validate_event(event, ["anime_id", "user_id", "duration_seconds", "occurred_at", "event_id"])
        
        if await self._is_event_processed(event_id):
            logger.info(f"Evento {event_id} ya fue procesado, saltando (idempotencia)")
            return
        
        try:
            anime_id = event["anime_id"]
            user_id = event["user_id"]
            duration_seconds = event["duration_seconds"]
            occurred_at = self._parse_ts(event["occurred_at"])
            
            if duration_seconds < 0:
                raise EventProcessingError(f"duration_seconds debe ser positivo, recibido: {duration_seconds}")
            
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("""
                        INSERT INTO anime_views (anime_id, user_id, total_duration_seconds, last_view_at)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (anime_id, user_id) DO UPDATE SET
                            view_count = anime_views.view_count + 1,
                            total_duration_seconds = anime_views.total_duration_seconds + EXCLUDED.total_duration_seconds,
                            last_view_at = EXCLUDED.last_view_at
                    """, anime_id, user_id, duration_seconds, occurred_at)
                    
                    await conn.execute("""
                        INSERT INTO anime_stats (anime_id, total_views, total_duration_seconds)
                        VALUES ($1, 1, $2)
                        ON CONFLICT (anime_id) DO UPDATE SET
                            total_views = anime_stats.total_views + 1,
                            total_duration_seconds = anime_stats.total_duration_seconds + EXCLUDED.total_duration_seconds,
                            updated_at = CURRENT_TIMESTAMP
                    """, anime_id, duration_seconds)
            
            duration_ms = int((time.time() - start_time) * 1000)
            await self._mark_event_processed(
                event_id, event_type, aggregate_id, duration_ms, 'success'
            )
            logger.info(
                f"Evento ViewRegistered procesado: anime_id={anime_id}, user_id={user_id}, "
                f"duration={duration_seconds}s, processing_time={duration_ms}ms"
            )
            
            if hasattr(self, '_repository') and self._repository:
                self._repository.invalidate_anime_cache(anime_id)

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            await self._mark_event_processed(
                event_id, event_type, aggregate_id, duration_ms, 'error', error_msg
            )
            logger.error(
                f"Error procesando evento ViewRegistered {event_id}: {e}",
                exc_info=True
            )
            raise EventProcessingError(f"Error procesando evento de visualización: {e}") from e
    
    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def process_rating_event(self, event: Dict[str, Any]):
        """Procesa un evento de calificación con validación e idempotencia."""
        start_time = time.time()
        event_id = event.get("event_id")
        event_type = event.get("event_type", "RatingGiven")
        aggregate_id = event.get("aggregate_id")
        
        self._validate_event(event, ["anime_id", "user_id", "rating", "occurred_at", "event_id"])
        
        if await self._is_event_processed(event_id):
            logger.info(f"Evento {event_id} ya fue procesado, saltando (idempotencia)")
            return
        
        try:
            anime_id = event["anime_id"]
            user_id = event["user_id"]
            rating = float(event["rating"])
            occurred_at = self._parse_ts(event["occurred_at"])
            
            if not (1.0 <= rating <= 10.0):
                raise EventProcessingError(f"Rating debe estar entre 1.0 y 10.0, recibido: {rating}")
            
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("""
                        INSERT INTO anime_ratings (anime_id, user_id, rating, rated_at)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (anime_id, user_id) DO UPDATE SET
                            rating = EXCLUDED.rating,
                            rated_at = EXCLUDED.rated_at
                    """, anime_id, user_id, rating, occurred_at)
                    
                    result = await conn.fetchrow("""
                        SELECT AVG(rating) as avg_rating, COUNT(*) as count
                        FROM anime_ratings
                        WHERE anime_id = $1
                    """, anime_id)
                    
                    avg_rating = float(result["avg_rating"]) if result["avg_rating"] else 0.0
                    count = result["count"]
                    
                    await conn.execute("""
                        INSERT INTO anime_stats (anime_id, total_ratings, average_rating)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (anime_id) DO UPDATE SET
                            total_ratings = EXCLUDED.total_ratings,
                            average_rating = EXCLUDED.average_rating,
                            updated_at = CURRENT_TIMESTAMP
                    """, anime_id, count, avg_rating)
            
            duration_ms = int((time.time() - start_time) * 1000)
            await self._mark_event_processed(
                event_id, event_type, aggregate_id, duration_ms, 'success'
            )
            logger.info(
                f"Evento RatingGiven procesado: anime_id={anime_id}, user_id={user_id}, "
                f"rating={rating}, avg_rating={avg_rating:.2f}, processing_time={duration_ms}ms"
            )
            
            if hasattr(self, '_repository') and self._repository:
                self._repository.invalidate_anime_cache(anime_id)

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            await self._mark_event_processed(
                event_id, event_type, aggregate_id, duration_ms, 'error', error_msg
            )
            logger.error(
                f"Error procesando evento RatingGiven {event_id}: {e}",
                exc_info=True
            )
            raise EventProcessingError(f"Error procesando evento de calificación: {e}") from e