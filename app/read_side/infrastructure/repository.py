"""Repositorio para acceder al read model."""
from typing import List, Optional
import asyncpg
from config.settings import settings
from common.utils.logger import get_logger
from common.utils.retry import retry_async
from common.utils.cache import InMemoryCache
from common.exceptions import AnimeNotFoundError


logger = get_logger(__name__)


class ReadModelRepository:
    """Repositorio para consultar el read model con manejo robusto de errores."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self._cache: Optional[InMemoryCache] = None
        if settings.CACHE_ENABLED:
            self._cache = InMemoryCache(default_ttl=settings.CACHE_DEFAULT_TTL)
            logger.info(f"Caché habilitado con TTL: {settings.CACHE_DEFAULT_TTL}s")
    
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
    
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Genera una clave de caché."""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"
    
    def invalidate_anime_cache(self, anime_id: int) -> None:
        """Invalida el caché de un anime específico."""
        if not self._cache:
            return
        
        patterns = [
            f"anime_stats:{anime_id}",
            f"anime:{anime_id}",
        ]
        
        for pattern in patterns:
            self._cache.delete(pattern)
        logger.debug(f"Caché invalidado para anime_id: {anime_id}")
    
    def get_cache_stats(self) -> Optional[dict]:
        """Obtiene estadísticas del caché."""
        if not self._cache or not settings.CACHE_STATS_ENABLED:
            return None
        return self._cache.get_stats()
    
    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def get_top_animes_by_views(self, limit: int = 10) -> List[dict]:
        """Obtiene los top animes por visualizaciones."""
        try:
            if not self._pool:
                raise RuntimeError("Repository no está conectado. Llama a connect() primero.")
            
            self._validate_limit(limit)
            
            cache_key = self._get_cache_key("top_views", limit)
            if self._cache:
                cached = self._cache.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache HIT para top_views (limit={limit})")
                    return cached
            
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
                results = [dict(row) for row in rows]
                
                if self._cache:
                    self._cache.set(cache_key, results)
                
                return results
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
            
            cache_key = self._get_cache_key("top_rating", limit)
            if self._cache:
                cached = self._cache.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache HIT para top_rating (limit={limit})")
                    return cached
            
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
                        AND total_ratings >= 5
                    ORDER BY average_rating DESC, total_ratings DESC
                    LIMIT $1
                """, limit)
                logger.debug(f"Se obtuvieron {len(rows)} resultados")
                results = [dict(row) for row in rows]
                
                if self._cache:
                    self._cache.set(cache_key, results)
                
                return results
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
            
            cache_key = self._get_cache_key("anime_stats", anime_id)
            if self._cache:
                cached = self._cache.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache HIT para anime_stats (anime_id={anime_id})")
                    return cached
            
            logger.debug(f"Obteniendo estadísticas del anime {anime_id}")
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM anime_stats
                    WHERE anime_id = $1
                """, anime_id)
                logger.debug(f"Se obtuvo la estadística del anime {anime_id}")
                result = dict(row) if row else None
                
                if self._cache and result:
                    self._cache.set(cache_key, result)
                
                return result
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
            
            cache_key = self._get_cache_key("anime", anime_id)
            if self._cache:
                cached = self._cache.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache HIT para anime (anime_id={anime_id})")
                    return cached
            
            logger.debug(f"Obteniendo anime {anime_id}")
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM animes
                    WHERE myanimelist_id = $1
                """, anime_id)
                logger.debug(f"Se obtuvo el anime {anime_id}")
                result = dict(row) if row else None
                
                if self._cache and result:
                    self._cache.set(cache_key, result)
                
                return result
        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo anime {anime_id}: {e}", exc_info=True)
            raise

    @retry_async(max_attempts=3, exceptions=(asyncpg.PostgresError,))
    async def get_trending_animes(self, days: int = 7, limit: int = 10) -> List[dict]:
        """Obtiene animes en tendencia combinando clicks, views y ratings recientes."""
        try:
            if not self._pool:
                raise RuntimeError("Repository no está conectado. Llama a connect() primero.")
            
            self._validate_limit(limit)
            
            async with self._pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        a.myanimelist_id,
                        a.title,
                        a.description,
                        a.image,
                        a.type,
                        a.episodes,
                        a.score,
                        a.popularity,
                        a.genres,
                        COALESCE(recent.clicks, 0) + COALESCE(recent.views, 0) + COALESCE(recent.ratings, 0) as total_interactions,
                        COALESCE(s.total_clicks, 0) as total_clicks,
                        COALESCE(s.total_views, 0) as total_views,
                        COALESCE(s.total_ratings, 0) as total_ratings,
                        s.average_rating
                    FROM animes a
                    LEFT JOIN anime_stats s ON a.myanimelist_id = s.anime_id
                    LEFT JOIN (
                        SELECT 
                            anime_id,
                            COUNT(*) FILTER (WHERE last_click_at >= NOW() - make_interval(days => $2)) as clicks,
                            COUNT(*) FILTER (WHERE last_view_at >= NOW() - make_interval(days => $2)) as views,
                            COUNT(*) FILTER (WHERE rated_at >= NOW() - make_interval(days => $2)) as ratings
                        FROM (
                            SELECT anime_id, last_click_at, NULL::timestamp as last_view_at, NULL::timestamp as rated_at FROM anime_clicks
                            UNION ALL
                            SELECT anime_id, NULL::timestamp, last_view_at, NULL::timestamp FROM anime_views
                            UNION ALL
                            SELECT anime_id, NULL::timestamp, NULL::timestamp, rated_at FROM anime_ratings
                        ) agg
                        GROUP BY anime_id
                    ) recent ON a.myanimelist_id = recent.anime_id
                    WHERE recent.clicks IS NOT NULL OR recent.views IS NOT NULL OR recent.ratings IS NOT NULL
                    ORDER BY total_interactions DESC, s.total_views DESC
                    LIMIT $1
                """, limit, days)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error obteniendo trending animes: {e}", exc_info=True)
            raise
