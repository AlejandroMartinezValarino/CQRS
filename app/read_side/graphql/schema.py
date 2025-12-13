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
class AnimeWithStats:
    """Anime completo con estadísticas integradas."""
    myanimelist_id: int
    title: str
    description: Optional[str]
    image: Optional[str]
    type: Optional[str]
    episodes: Optional[int]
    score: Optional[float]
    popularity: Optional[int]
    genres: Optional[str]
    total_clicks: int = 0
    total_views: int = 0
    total_ratings: int = 0
    average_rating: Optional[float] = None


@strawberry.type
class PaginatedAnimes:
    """Respuesta paginada de animes."""
    items: List[AnimeWithStats]
    total: int
    page: int
    page_size: int
    has_more: bool


@strawberry.input
class AnimeFilters:
    """Filtros para búsqueda de animes."""
    search: Optional[str] = None
    type: Optional[str] = None
    genres: Optional[List[str]] = None
    min_score: Optional[float] = None
    sort_by: Optional[str] = "popularity"


@strawberry.type
class Query:
    """Queries GraphQL."""
    
    @strawberry.field
    async def top_animes_by_views(self, limit: int = 10) -> List[AnimeStats]:
        """Obtiene los top animes por visualizaciones."""
        try:
            self._validate_limit(limit)
            repo = get_repository()
            results = await repo.get_top_animes_by_views(limit)
            logger.debug(f"Se obtuvieron {len(results)} resultados")
            return [self._row_to_anime_stats(row) for row in results]
        except ValueError as e:
            logger.error(f"Error al obtener los top animes por visualizaciones: {e}", exc_info=True)
            raise InvalidLimitError(str(e))
        except Exception as e:
            logger.error(f"Error al obtener los top animes por visualizaciones: {e}", exc_info=True)
            raise GraphQLError(str(e))
    
    def _row_to_anime_stats(self, row: dict) -> AnimeStats:
        """Helper para transformar una fila a AnimeStats (evita duplicación)."""
        return AnimeStats(
            anime_id=row["anime_id"],
            total_clicks=row["total_clicks"] or 0,
            total_views=row["total_views"] or 0,
            total_ratings=row["total_ratings"] or 0,
            average_rating=float(row["average_rating"]) if row["average_rating"] else None,
            total_duration_seconds=row["total_duration_seconds"] or 0,
        )

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
    
    @strawberry.field
    async def top_animes_by_rating(self, limit: int = 10) -> List[AnimeStats]:
        """Obtiene los top animes por calificación promedio."""
        try:
            self._validate_limit(limit)
            repo = get_repository()
            results = await repo.get_top_animes_by_rating(limit)
            logger.debug(f"Se obtuvieron {len(results)} resultados")
            return [self._row_to_anime_stats(row) for row in results]
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
            self._validate_anime_id(anime_id)
            repo = get_repository()
            row = await repo.get_anime_stats(anime_id)
            if not row:
                return None
            logger.debug(f"Se obtuvo la estadística del anime {anime_id}")
            return self._row_to_anime_stats(row)
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
            self._validate_anime_id(anime_id)
            repo = get_repository()
            row = await repo.get_anime(anime_id)
            if not row:
                return None
            logger.debug(f"Se obtuvo el anime {anime_id}")
            return self._row_to_anime(row)
        except ValueError as e:
            logger.error(f"Error al obtener el anime {anime_id}: {e}", exc_info=True)
            raise AnimeNotFoundError(anime_id)
        except Exception as e:
            logger.error(f"Error al obtener el anime {anime_id}: {e}", exc_info=True)
            raise GraphQLError(str(e))

    def _row_to_anime(self, row: dict) -> Anime:
        """Helper para transformar una fila a Anime (evita duplicación)."""
        return Anime(
            myanimelist_id=row["myanimelist_id"],
            title=row["title"],
            description=row.get("description"),
            image=row.get("image"),
            type=row.get("type"),
            episodes=row.get("episodes"),
            score=float(row["score"]) if row.get("score") else None,
    def _row_to_anime(self, row: dict) -> Anime:
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
    
    def _row_to_anime_with_stats(self, row: dict) -> AnimeWithStats:
        return AnimeWithStats(
            myanimelist_id=row["myanimelist_id"],
            title=row["title"],
            description=row.get("description"),
            image=row.get("image"),
            type=row.get("type"),
            episodes=row.get("episodes"),
            score=float(row["score"]) if row.get("score") else None,
            popularity=row.get("popularity"),
            genres=row.get("genres"),
            total_clicks=row.get("total_clicks", 0),
            total_views=row.get("total_views", 0),
            total_ratings=row.get("total_ratings", 0),
            average_rating=float(row["average_rating"]) if row.get("average_rating") else None,
        )

    @strawberry.field
    async def search_animes(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[AnimeFilters] = None
    ) -> PaginatedAnimes:
        try:
            repo = get_repository()
            results, total = await repo.search_animes(
                search=filters.search if filters else None,
                anime_type=filters.type if filters else None,
                genres=filters.genres if filters else None,
                min_score=filters.min_score if filters else None,
                sort_by=filters.sort_by if filters else "popularity",
                page=page,
                page_size=page_size
            )
            
            items = [self._row_to_anime_with_stats(row) for row in results]
            has_more = (page * page_size) < total
            
            return PaginatedAnimes(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                has_more=has_more
            )
        except Exception as e:
            logger.error(f"Error buscando animes: {e}", exc_info=True)
            raise GraphQLError(str(e))
    
    @strawberry.field
    async def trending_animes(self, limit: int = 10, days: int = 7) -> List[AnimeWithStats]:
        try:
            self._validate_limit(limit)
            repo = get_repository()
            results = await repo.get_trending_animes(days=days, limit=limit)
            return [self._row_to_anime_with_stats(row) for row in results]
        except Exception as e:
            logger.error(f"Error obteniendo trending animes: {e}", exc_info=True)
            raise GraphQLError(str(e))
    
    @strawberry.field
    async def recommended_animes(
        self,
        based_on_anime_id: int,
        limit: int = 10
    ) -> List[AnimeWithStats]:
        try:
            self._validate_anime_id(based_on_anime_id)
            self._validate_limit(limit)
            repo = get_repository()
            results = await repo.get_recommended_animes(anime_id=based_on_anime_id, limit=limit)
            return [self._row_to_anime_with_stats(row) for row in results]
        except Exception as e:
            logger.error(f"Error obteniendo recomendaciones: {e}", exc_info=True)
            raise GraphQLError(str(e))
    
    @strawberry.field
    async def genres(self) -> List[str]:
        try:
            repo = get_repository()
            return await repo.get_all_genres()
        except Exception as e:
            logger.error(f"Error obteniendo géneros: {e}", exc_info=True)
            raise GraphQLError(str(e))


schema = strawberry.Schema(query=Query)

