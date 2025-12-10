"""Repositorio para acceder al read model."""
from typing import List, Optional
import asyncpg
from config.settings import settings
from common.utils.logger import get_logger
from common.utils.retry import retry_async
from common.exceptions import AnimeNotFoundError


logger = get_logger(__name__)


class ReadModelRepository:
    """Repositorio para consultar el read model con manejo robusto de errores."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Crea el pool de conexiones con configuración optimizada."""
        try:
            self._pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=settings.POSTGRES_MIN_CONNECTIONS,
                max_size=settings.POSTGRES_MAX_CONNECTIONS,
                command_timeout=settings.POSTGRES_COMMAND_TIMEOUT,
            )
            logger.info("Pool de conexiones del ReadModelRepository creado correctamente")
        except Exception as e:
            logger.error(f"Error creando pool de conexiones: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Cierra el pool."""
        if self._pool:
            try:
                await self._pool.close()
                logger.info("Pool de conexiones del ReadModelRepository cerrado")
            except Exception as e:
                logger.error(f"Error cerrando pool: {e}", exc_info=True)
    
    def _validate_limit(self, limit: int) -> None:
        """Valida que el límite esté en un rango válido."""
        if limit < 1:
            raise ValueError("El límite debe ser mayor a 0")
        if limit > 100:
            raise ValueError("El límite no puede ser mayor a 100")
    
    def _validate_anime_id(self, anime_id: int) -> None:
        """Valida que el anime_id sea válido."""
        if anime_id < 1:
            raise ValueError("El anime_id debe ser mayor a 0")
    
    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def get_top_animes_by_views(self, limit: int = 10) -> List[dict]:
        """Obtiene los top animes por visualizaciones."""
        try:
            if not self._pool:
                raise RuntimeError("Repository no está conectado. Llama a connect() primero.")
            
            self._validate_limit(limit)
            logger.debug(f"Obteniendo top {limit} animes por visualizaciones")
            async with self._pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        anime_id,
                        total_clicks,
                        total_views,
                        total_ratings,
                        average_rating,
                        total_duration_seconds
                    FROM anime_stats
                    WHERE total_views > 0
                    ORDER BY total_views DESC
                    LIMIT $1
                """, limit)
                logger.debug(f"Se obtuvieron {len(rows)} resultados")
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error obteniendo top {limit} animes por visualizaciones: {e}", exc_info=True)
            raise
    
    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def get_top_animes_by_rating(self, limit: int = 10) -> List[dict]:
        """Obtiene los top animes por calificación promedio."""
        try:
            if not self._pool:
                raise RuntimeError("Repository no está conectado. Llama a connect() primero.")
            
            self._validate_limit(limit)
            logger.debug(f"Obteniendo top {limit} animes por calificación promedio")
            async with self._pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        anime_id,
                        total_clicks,
                        total_views,
                        total_ratings,
                        average_rating,
                        total_duration_seconds
                    FROM anime_stats
                    WHERE average_rating > 0 
                        AND total_ratings >= 5  -- Solo animes con al menos 5 calificaciones
                    ORDER BY average_rating DESC, total_ratings DESC
                    LIMIT $1
                """, limit)
                logger.debug(f"Se obtuvieron {len(rows)} resultados")
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error obteniendo top {limit} animes por calificación promedio: {e}", exc_info=True)
            raise
    
    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def get_anime_stats(self, anime_id: int) -> Optional[dict]:
        """Obtiene las estadísticas de un anime específico."""
        try:
            if not self._pool:
                raise RuntimeError("Repository no está conectado. Llama a connect() primero.")
            
            self._validate_anime_id(anime_id)
            logger.debug(f"Obteniendo estadísticas del anime {anime_id}")
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM anime_stats
                    WHERE anime_id = $1
                """, anime_id)
                logger.debug(f"Se obtuvo la estadística del anime {anime_id}")
                return dict(row) if row else None
        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del anime {anime_id}: {e}", exc_info=True)
            raise
    
    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def get_anime(self, anime_id: int) -> Optional[dict]:
        """Obtiene un anime por ID."""
        try:
            if not self._pool:
                raise RuntimeError("Repository no está conectado. Llama a connect() primero.")
            self._validate_anime_id(anime_id)
            logger.debug(f"Obteniendo anime {anime_id}")
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM animes
                    WHERE myanimelist_id = $1
                """, anime_id)
                logger.debug(f"Se obtuvo el anime {anime_id}")
                return dict(row) if row else None
        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo anime {anime_id}: {e}", exc_info=True)
            raise