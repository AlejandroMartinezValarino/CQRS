"""Script para verificar conexión a la base de datos."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
import asyncpg


async def check_connection():
    """Verifica la conexión a PostgreSQL."""
    try:
        conn = await asyncpg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )
        await conn.close()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    if asyncio.run(check_connection()):
        sys.exit(0)
    else:
        sys.exit(1)
