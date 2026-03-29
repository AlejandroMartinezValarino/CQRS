"""Rellena anime_stats a partir de la tabla animes para que el front muestre listados sin eventos previos.

El CSV (`load_mal_to_postgres`) solo inserta en `animes`. Las vistas GraphQL de ranking leen
`anime_stats`, que en producción se actualiza con el consumer a partir de Kafka. Este script
inserta estadísticas mínimas (p. ej. total_views = 1) para demos y desarrollo.
"""
import asyncio
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

import asyncpg
from config.settings import settings


async def main() -> None:
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
    )
    try:
        n = await conn.execute(
            """
            INSERT INTO anime_stats (
                anime_id, total_clicks, total_views, total_ratings,
                average_rating, total_duration_seconds
            )
            SELECT
                myanimelist_id,
                0,
                1,
                0,
                0,
                0
            FROM animes
            ON CONFLICT (anime_id) DO UPDATE SET
                total_views = GREATEST(anime_stats.total_views, EXCLUDED.total_views)
            """
        )
        print(f"Listo: {n}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
