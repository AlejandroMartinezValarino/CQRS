"""Script para verificar conexión a la base de datos."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from common.utils.db import get_pool_kwargs
import asyncpg


async def check_connection():
    """Verifica la conexión a PostgreSQL."""
    try:
        pool_kwargs = get_pool_kwargs(database=settings.POSTGRES_DB)
        conn = await asyncpg.connect(**pool_kwargs)
        await conn.close()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    if asyncio.run(check_connection()):
        sys.exit(0)
    else:
        sys.exit(1)
