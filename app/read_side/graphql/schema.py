"""Schema GraphQL."""
import strawberry
from typing import List, Optional
from app.read_side.infrastructure.repository import ReadModelRepository
from app.read_side.graphql.exceptions import InvalidLimitError
from common.utils.logger import get_logger
from common.exceptions import GraphQLError, AnimeNotFoundError

logger = get_logger(__name__)
_repository: Optional[ReadModelRepository] = None


def get_repository() -> ReadModelRepository:
    """Obtiene la instancia del repositorio."""
    global _repository
    if _repository is None:
        _repository = ReadModelRepository()
    return _repository


def _validate_limit(limit: int) -> None:
    """Valida que el límite esté en un rango válido."""
    if limit < 1:
        raise ValueError("El límite debe ser mayor a 0")
    if limit > 100:
        raise ValueError("El límite no puede ser mayor a 100")


def _validate_anime_id(anime_id: int) -> None:
    """Valida que el anime_id sea válido."""
    if anime_id < 1:
        raise ValueError("El anime_id debe ser mayor a 0")


def _row_to_anime_stats(row: dict) -> "AnimeStats":
    return AnimeStats(
        anime_id=row["anime_id"],
        total_clicks=row["total_clicks"] or 0,
        total_views=row["total_views"] or 0,
        total_ratings=row["total_ratings"] or 0,
        average_rating=float(row["average_rating"]) if row["average_rating"] else None,
        total_duration_seconds=row["total_duration_seconds"] or 0,
        title=row.get("title"),
        image=row.get("image"),
    )


def _row_to_anime(row: dict) -> "Anime":
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
    title: Optional[str] = None
    image: Optional[str] = None


@strawberry.type
class Query:
    """Queries GraphQL."""

    @strawberry.field
    async def top_animes_by_views(self, limit: int = 10) -> List[AnimeStats]:
        """Obtiene los top animes por visualizaciones."""
        try:
            _validate_limit(limit)
            repo = get_repository()
            results = await repo.get_top_animes_by_views(limit)
            logger.debug(f"Se obtuvieron {len(results)} resultados")
            return [_row_to_anime_stats(row) for row in results]
        except ValueError as e:
            logger.error(f"Error al obtener los top animes por visualizaciones: {e}", exc_info=True)
            raise InvalidLimitError(str(e))
        except Exception as e:
            logger.error(f"Error al obtener los top animes por visualizaciones: {e}", exc_info=True)
            raise GraphQLError(str(e))

    @strawberry.field
    async def top_animes_by_rating(self, limit: int = 10) -> List[AnimeStats]:
        """Obtiene los top animes por calificación promedio."""
        try:
            _validate_limit(limit)
            repo = get_repository()
            results = await repo.get_top_animes_by_rating(limit)
            logger.debug(f"Se obtuvieron {len(results)} resultados")
            return [_row_to_anime_stats(row) for row in results]
        except ValueError as e:
            logger.error(f"Error al obtener los top animes por calificación promedio: {e}", exc_info=True)
            raise InvalidLimitError(str(e))
        except Exception as e:
            logger.error(f"Error al obtener los top animes por calificación promedio: {e}", exc_info=True)
            raise GraphQLError(str(e))

    @strawberry.field
    async def anime_stats(self, anime_id: int) -> Optional[AnimeStats]:
        """Obtiene las estadísticas de un anime específico."""
        try:
            _validate_anime_id(anime_id)
            repo = get_repository()
            row = await repo.get_anime_stats(anime_id)
            if not row:
                return None
            logger.debug(f"Se obtuvo la estadística del anime {anime_id}")
            return _row_to_anime_stats(row)
        except ValueError as e:
            logger.error(f"Error al obtener las estadísticas del anime {anime_id}: {e}", exc_info=True)
            raise AnimeNotFoundError(anime_id)
        except Exception as e:
            logger.error(f"Error al obtener las estadísticas del anime {anime_id}: {e}", exc_info=True)
            raise GraphQLError(str(e))

    @strawberry.field
    async def anime(self, anime_id: int) -> Optional[Anime]:
        """Obtiene un anime por ID."""
        try:
            _validate_anime_id(anime_id)
            repo = get_repository()
            row = await repo.get_anime(anime_id)
            if not row:
                return None
            logger.debug(f"Se obtuvo el anime {anime_id}")
            return _row_to_anime(row)
        except ValueError as e:
            logger.error(f"Error al obtener el anime {anime_id}: {e}", exc_info=True)
            raise AnimeNotFoundError(anime_id)
        except Exception as e:
            logger.error(f"Error al obtener el anime {anime_id}: {e}", exc_info=True)
            raise GraphQLError(str(e))


schema = strawberry.Schema(query=Query)
