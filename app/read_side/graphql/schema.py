"""Schema GraphQL."""
import strawberry
from typing import List, Optional
from app.read_side.infrastructure.repository import ReadModelRepository

# Instancia global del repositorio (se inicializará en el startup)
_repository: Optional[ReadModelRepository] = None


def get_repository() -> ReadModelRepository:
    """Obtiene la instancia del repositorio."""
    global _repository
    if _repository is None:
        _repository = ReadModelRepository()
    return _repository


@strawberry.type
class Anime:
    """Tipo GraphQL para Anime."""
    myanimelist_id: int
    title: str
    description: Optional[str]
    image: Optional[str]
    type: Optional[str]
    episodes: Optional[int]
    score: Optional[float]
    popularity: Optional[int]


@strawberry.type
class AnimeStats:
    """Estadísticas de un anime."""
    anime_id: int
    total_clicks: int
    total_views: int
    total_ratings: int
    average_rating: Optional[float]
    total_duration_seconds: int


@strawberry.type
class Query:
    """Queries GraphQL."""
    
    @strawberry.field
    async def top_animes_by_views(self, limit: int = 10) -> List[AnimeStats]:
        """Obtiene los top animes por visualizaciones."""
        repo = get_repository()
        results = await repo.get_top_animes_by_views(limit)
        return [
            AnimeStats(
                anime_id=row["anime_id"],
                total_clicks=row["total_clicks"] or 0,
                total_views=row["total_views"] or 0,
                total_ratings=row["total_ratings"] or 0,
                average_rating=float(row["average_rating"]) if row["average_rating"] else None,
                total_duration_seconds=row["total_duration_seconds"] or 0,
            )
            for row in results
        ]
    
    @strawberry.field
    async def top_animes_by_rating(self, limit: int = 10) -> List[AnimeStats]:
        """Obtiene los top animes por calificación promedio."""
        repo = get_repository()
        results = await repo.get_top_animes_by_rating(limit)
        return [
            AnimeStats(
                anime_id=row["anime_id"],
                total_clicks=row["total_clicks"] or 0,
                total_views=row["total_views"] or 0,
                total_ratings=row["total_ratings"] or 0,
                average_rating=float(row["average_rating"]) if row["average_rating"] else None,
                total_duration_seconds=row["total_duration_seconds"] or 0,
            )
            for row in results
        ]
    
    @strawberry.field
    async def anime_stats(self, anime_id: int) -> Optional[AnimeStats]:
        """Obtiene las estadísticas de un anime específico."""
        repo = get_repository()
        row = await repo.get_anime_stats(anime_id)
        if not row:
            return None
        return AnimeStats(
            anime_id=row["anime_id"],
            total_clicks=row["total_clicks"] or 0,
            total_views=row["total_views"] or 0,
            total_ratings=row["total_ratings"] or 0,
            average_rating=float(row["average_rating"]) if row["average_rating"] else None,
            total_duration_seconds=row["total_duration_seconds"] or 0,
        )
    
    @strawberry.field
    async def anime(self, anime_id: int) -> Optional[Anime]:
        """Obtiene un anime por ID."""
        repo = get_repository()
        row = await repo.get_anime(anime_id)
        if not row:
            return None
        return Anime(
            myanimelist_id=row["myanimelist_id"],
            title=row["title"],
            description=row.get("description"),
            image=row.get("image"),
            type=row.get("type"),
            episodes=row.get("episodes"),
            score=float(row["score"]) if row.get("score") else None,
            popularity=row.get("popularity"),
        )


schema = strawberry.Schema(query=Query)

