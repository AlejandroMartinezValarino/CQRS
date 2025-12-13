"""Script para cargar el dataset de MAL desde CSV a PostgreSQL."""
import asyncio
import csv
import json
import sys
import os
from pathlib import Path
from typing import Optional
import asyncpg

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


async def create_table(conn: asyncpg.Connection):
    """Crea la tabla de animes si no existe."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS animes (
            myanimelist_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            image TEXT,
            type TEXT,
            episodes INTEGER,
            status TEXT,
            premiered TEXT,
            released_season TEXT,
            released_year NUMERIC,
            source TEXT,
            genres TEXT,
            themes TEXT,
            studios TEXT,
            producers TEXT,
            demographic TEXT,
            duration TEXT,
            rating TEXT,
            score NUMERIC,
            ranked INTEGER,
            popularity INTEGER,
            members INTEGER,
            favorites INTEGER,
            characters JSONB,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_animes_title ON animes(title);
        CREATE INDEX IF NOT EXISTS idx_animes_score ON animes(score);
        CREATE INDEX IF NOT EXISTS idx_animes_popularity ON animes(popularity);
    """)


def parse_value(value: str, field_type: str) -> Optional[any]:
    """Parsea un valor del CSV según su tipo."""
    if not value or value.strip() == "":
        return None
    
    value = value.strip()
    
    if field_type == "int":
        try:
            # Manejar valores con comas (ej: "2,008,019")
            return int(value.replace(",", ""))
        except (ValueError, AttributeError):
            return None
    elif field_type == "float":
        try:
            return float(value)
        except (ValueError, AttributeError):
            return None
    elif field_type == "json":
        try:
            return json.loads(value)
        except (json.JSONDecodeError, AttributeError):
            return None
    else:
        return value


async def load_csv_to_db(csv_path: Path, batch_size: int = 100):
    """Carga el CSV a PostgreSQL."""
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
    )
    
    try:
        await create_table(conn)
        
        # Leer CSV
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch = []
            total_inserted = 0
            
            for row in reader:
                # Parsear valores
                anime_data = {
                    "myanimelist_id": parse_value(row.get("myanimelist_id", ""), "int"),
                    "title": parse_value(row.get("title", ""), "str"),
                    "description": parse_value(row.get("description", ""), "str"),
                    "image": parse_value(row.get("image", ""), "str"),
                    "type": parse_value(row.get("Type", ""), "str"),
                    "episodes": parse_value(row.get("Episodes", ""), "float"),
                    "status": parse_value(row.get("Status", ""), "str"),
                    "premiered": parse_value(row.get("Premiered", ""), "str"),
                    "released_season": parse_value(row.get("Released_Season", ""), "str"),
                    "released_year": parse_value(row.get("Released_Year", ""), "float"),
                    "source": parse_value(row.get("Source", ""), "str"),
                    "genres": parse_value(row.get("Genres", ""), "str"),
                    "themes": parse_value(row.get("Themes", ""), "str"),
                    "studios": parse_value(row.get("Studios", ""), "str"),
                    "producers": parse_value(row.get("Producers", ""), "str"),
                    "demographic": parse_value(row.get("Demographic", ""), "str"),
                    "duration": parse_value(row.get("Duration", ""), "str"),
                    "rating": parse_value(row.get("Rating", ""), "str"),
                    "score": parse_value(row.get("Score", ""), "float"),
                    "ranked": parse_value(row.get("Ranked", ""), "int"),
                    "popularity": parse_value(row.get("Popularity", ""), "int"),
                    "members": parse_value(row.get("Members", ""), "int"),
                    "favorites": parse_value(row.get("Favorites", ""), "int"),
                    "characters": parse_value(row.get("characters", ""), "json"),
                    "source_url": parse_value(row.get("source_url", ""), "str"),
                }
                
                batch.append(anime_data)
                
                if len(batch) >= batch_size:
                    await insert_batch(conn, batch)
                    total_inserted += len(batch)
                    print(f"Insertados {total_inserted} registros...")
                    batch = []
            
            # Insertar el último batch
            if batch:
                await insert_batch(conn, batch)
                total_inserted += len(batch)
            
            print(f"Total de registros insertados: {total_inserted}")
    
    finally:
        await conn.close()


async def insert_batch(conn: asyncpg.Connection, batch: list):
    """Inserta un batch de registros."""
    await conn.executemany("""
        INSERT INTO animes (
            myanimelist_id, title, description, image, type, episodes,
            status, premiered, released_season, released_year, source,
            genres, themes, studios, producers, demographic, duration,
            rating, score, ranked, popularity, members, favorites,
            characters, source_url
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
            $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24
        ) ON CONFLICT (myanimelist_id) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            image = EXCLUDED.image,
            type = EXCLUDED.type,
            episodes = EXCLUDED.episodes,
            status = EXCLUDED.status,
            premiered = EXCLUDED.premiered,
            released_season = EXCLUDED.released_season,
            released_year = EXCLUDED.released_year,
            source = EXCLUDED.source,
            genres = EXCLUDED.genres,
            themes = EXCLUDED.themes,
            studios = EXCLUDED.studios,
            producers = EXCLUDED.producers,
            demographic = EXCLUDED.demographic,
            duration = EXCLUDED.duration,
            rating = EXCLUDED.rating,
            score = EXCLUDED.score,
            ranked = EXCLUDED.ranked,
            popularity = EXCLUDED.popularity,
            members = EXCLUDED.members,
            favorites = EXCLUDED.favorites,
            characters = EXCLUDED.characters,
            source_url = EXCLUDED.source_url
    """, [
        (
            item["myanimelist_id"],
            item["title"],
            item["description"],
            item["image"],
            item["type"],
            int(item["episodes"]) if item["episodes"] else None,
            item["status"],
            item["premiered"],
            item["released_season"],
            float(item["released_year"]) if item["released_year"] else None,
            item["source"],
            item["genres"],
            item["themes"],
            item["studios"],
            item["producers"],
            item["demographic"],
            item["duration"],
            item["rating"],
            item["score"],
            item["ranked"],
            item["popularity"],
            item["members"],
            item["favorites"],
            json.dumps(item["characters"]) if item["characters"] else None,
            item["source_url"],
        )
        for item in batch
    ])


async def main():
    """Función principal."""
    csv_path = Path(__file__).parent.parent / "data" / "mal_anime.csv"
    
    if not csv_path.exists():
        print(f"Error: No se encuentra el archivo {csv_path}")
        return
    
    print(f"Cargando datos desde {csv_path}...")
    await load_csv_to_db(csv_path)
    print("Carga completada!")


if __name__ == "__main__":
    asyncio.run(main())

