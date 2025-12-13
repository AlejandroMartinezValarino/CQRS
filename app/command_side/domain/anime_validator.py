from typing import Optional
import asyncpg
from common.utils.logger import get_logger
from common.utils.db import get_pool_kwargs
from config.settings import settings

logger = get_logger(__name__)

class AnimeValidator:
    """Valida reglas de negocio relacionadas con animes."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def _get_pool(self):
        """Obtiene el pool de conexiones."""
        if not self._pool:
            pool_kwargs = get_pool_kwargs(database=settings.POSTGRES_DB)
            self._pool = await asyncpg.create_pool(**pool_kwargs)
        return self._pool
    
    async def anime_exists(self, anime_id: int) -> bool:
        """Verifica si un anime existe en la base de datos."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM animes WHERE myanimelist_id = $1)",
                anime_id
            )
            return result
    
    async def close(self):
        """Cierra el pool."""
        if self._pool:
            await self._pool.close()