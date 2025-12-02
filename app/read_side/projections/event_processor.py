"""Procesador de eventos para actualizar proyecciones."""
from typing import Dict, Any
import asyncpg
from common.events.anime_events import ClickRegistered, ViewRegistered, RatingGiven
from config.settings import settings


class EventProcessor:
    """Procesa eventos y actualiza las proyecciones."""
    
    def __init__(self):
        self._pool: asyncpg.Pool = None
    
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
    
    async def process_click_event(self, event: Dict[str, Any]):
        """Procesa un evento de click."""
        anime_id = event["anime_id"]
        user_id = event["user_id"]
        occurred_at = event["occurred_at"]
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Actualizar tabla de clicks
                await conn.execute("""
                    INSERT INTO anime_clicks (anime_id, user_id, last_click_at)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (anime_id, user_id) DO UPDATE SET
                        click_count = anime_clicks.click_count + 1,
                        last_click_at = EXCLUDED.last_click_at
                """, anime_id, user_id, occurred_at)
                
                # Actualizar estadísticas agregadas
                await conn.execute("""
                    INSERT INTO anime_stats (anime_id, total_clicks)
                    VALUES ($1, 1)
                    ON CONFLICT (anime_id) DO UPDATE SET
                        total_clicks = anime_stats.total_clicks + 1,
                        updated_at = CURRENT_TIMESTAMP
                """, anime_id)
    
    async def process_view_event(self, event: Dict[str, Any]):
        """Procesa un evento de visualización."""
        anime_id = event["anime_id"]
        user_id = event["user_id"]
        duration_seconds = event["duration_seconds"]
        occurred_at = event["occurred_at"]
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Actualizar tabla de views
                await conn.execute("""
                    INSERT INTO anime_views (anime_id, user_id, total_duration_seconds, last_view_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (anime_id, user_id) DO UPDATE SET
                        view_count = anime_views.view_count + 1,
                        total_duration_seconds = anime_views.total_duration_seconds + EXCLUDED.total_duration_seconds,
                        last_view_at = EXCLUDED.last_view_at
                """, anime_id, user_id, duration_seconds, occurred_at)
                
                # Actualizar estadísticas agregadas
                await conn.execute("""
                    INSERT INTO anime_stats (anime_id, total_views, total_duration_seconds)
                    VALUES ($1, 1, $2)
                    ON CONFLICT (anime_id) DO UPDATE SET
                        total_views = anime_stats.total_views + 1,
                        total_duration_seconds = anime_stats.total_duration_seconds + EXCLUDED.total_duration_seconds,
                        updated_at = CURRENT_TIMESTAMP
                """, anime_id, duration_seconds)
    
    async def process_rating_event(self, event: Dict[str, Any]):
        """Procesa un evento de calificación."""
        anime_id = event["anime_id"]
        user_id = event["user_id"]
        rating = event["rating"]
        occurred_at = event["occurred_at"]
        
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Actualizar tabla de ratings
                await conn.execute("""
                    INSERT INTO anime_ratings (anime_id, user_id, rating, rated_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (anime_id, user_id) DO UPDATE SET
                        rating = EXCLUDED.rating,
                        rated_at = EXCLUDED.rated_at
                """, anime_id, user_id, rating, occurred_at)
                
                # Calcular promedio y actualizar estadísticas
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

