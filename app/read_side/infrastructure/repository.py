"""Repositorio para acceder al read model."""
from typing import List, Optional
import asyncpg
from config.settings import settings


class ReadModelRepository:
    """Repositorio para consultar el read model."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Crea el pool de conexiones."""
        self._pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
        )
    
    async def close(self):
        """Cierra el pool."""
        if self._pool:
            await self._pool.close()
    
    async def get_top_animes_by_views(self, limit: int = 10) -> List[dict]:
        """Obtiene los top animes por visualizaciones."""
        if not self._pool:
            await self.connect()
        
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
                ORDER BY total_views DESC
                LIMIT $1
            """, limit)
            
            return [dict(row) for row in rows]
    
    async def get_top_animes_by_rating(self, limit: int = 10) -> List[dict]:
        """Obtiene los top animes por calificación promedio."""
        if not self._pool:
            await self.connect()
        
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
                ORDER BY average_rating DESC, total_ratings DESC
                LIMIT $1
            """, limit)
            
            return [dict(row) for row in rows]
    
    async def get_anime_stats(self, anime_id: int) -> Optional[dict]:
        """Obtiene las estadísticas de un anime."""
        if not self._pool:
            await self.connect()
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    anime_id,
                    total_clicks,
                    total_views,
                    total_ratings,
                    average_rating,
                    total_duration_seconds
                FROM anime_stats
                WHERE anime_id = $1
            """, anime_id)
            
            return dict(row) if row else None
    
    async def get_anime(self, anime_id: int) -> Optional[dict]:
        """Obtiene un anime por ID."""
        if not self._pool:
            await self.connect()
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    myanimelist_id,
                    title,
                    description,
                    image,
                    type,
                    episodes,
                    score,
                    popularity
                FROM animes
                WHERE myanimelist_id = $1
            """, anime_id)
            
            return dict(row) if row else None

