"""Tests para GraphQL Schema."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.read_side.graphql.schema import Query, get_repository
from app.read_side.infrastructure.repository import ReadModelRepository
from app.read_side.graphql.exceptions import InvalidLimitError
from common.exceptions import AnimeNotFoundError, GraphQLError


@pytest.fixture
def mock_repository():
    """Fixture para mock del repositorio."""
    repo = MagicMock(spec=ReadModelRepository)
    return repo


@pytest.fixture
def query():
    """Fixture para Query GraphQL."""
    return Query()


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, 101])
async def test_top_animes_by_views_invalid_limit(query, limit):
    """Test que top_animes_by_views valida el límite."""
    with pytest.raises(InvalidLimitError):
        await query.top_animes_by_views(limit)


@pytest.mark.asyncio
async def test_top_animes_by_views_success(query, mock_repository):
    """Test que top_animes_by_views retorna resultados correctos."""
    with patch("app.read_side.graphql.schema.get_repository", return_value=mock_repository):
        mock_repository.get_top_animes_by_views = AsyncMock(return_value=[
            {
                "anime_id": 1,
                "total_clicks": 50,
                "total_views": 100,
                "total_ratings": 10,
                "average_rating": 8.5,
                "total_duration_seconds": 3600
            }
        ])
        results = await query.top_animes_by_views(10)
        assert len(results) == 1
        assert results[0].anime_id == 1
        assert results[0].total_clicks == 50
        assert results[0].total_views == 100
        assert results[0].total_ratings == 10
        assert results[0].average_rating == 8.5
        assert results[0].total_duration_seconds == 3600


@pytest.mark.asyncio
async def test_anime_stats_not_found(query, mock_repository):
    """Test que anime_stats retorna None cuando no encuentra el anime."""
    with patch("app.read_side.graphql.schema.get_repository", return_value=mock_repository):
        mock_repository.get_anime_stats = AsyncMock(return_value=None)
        result = await query.anime_stats(1)
        assert result is None


@pytest.mark.asyncio
async def test_anime_stats_success(query, mock_repository):
    """Test que anime_stats retorna resultados correctos."""
    with patch("app.read_side.graphql.schema.get_repository", return_value=mock_repository):
        mock_repository.get_anime_stats = AsyncMock(return_value={
            "anime_id": 1,
            "total_clicks": 50,
            "total_views": 100,
            "total_ratings": 10,
            "average_rating": 8.5,
            "total_duration_seconds": 3600
        })
        result = await query.anime_stats(1)
        assert result is not None
        assert result.anime_id == 1
        assert result.total_views == 100
        assert result.average_rating == 8.5


@pytest.mark.asyncio
async def test_anime_not_found(query, mock_repository):
    """Test que anime retorna None cuando no encuentra el anime."""
    with patch("app.read_side.graphql.schema.get_repository", return_value=mock_repository):
        mock_repository.get_anime = AsyncMock(return_value=None)
        result = await query.anime(1)
        assert result is None


@pytest.mark.asyncio
async def test_anime_success(query, mock_repository):
    """Test que anime retorna resultados correctos."""
    with patch("app.read_side.graphql.schema.get_repository", return_value=mock_repository):
        mock_repository.get_anime = AsyncMock(return_value={
            "myanimelist_id": 1,
            "title": "Test Anime",
            "description": "Test description",
            "image": "test.jpg",
            "type": "TV",
            "episodes": 12,
            "score": 8.5,
            "popularity": 100
        })
        result = await query.anime(1)
        assert result is not None
        assert result.myanimelist_id == 1
        assert result.title == "Test Anime"
        assert result.episodes == 12
        assert result.score == 8.5


@pytest.mark.asyncio
async def test_row_to_anime_stats(query):
    """Test del helper _row_to_anime_stats."""
    row = {
        "anime_id": 1,
        "total_clicks": 50,
        "total_views": 100,
        "total_ratings": 10,
        "average_rating": 8.5,
        "total_duration_seconds": 3600
    }
    result = query._row_to_anime_stats(row)
    assert result.anime_id == 1
    assert result.total_clicks == 50
    assert result.total_views == 100
    assert result.total_ratings == 10
    assert result.average_rating == 8.5
    assert result.total_duration_seconds == 3600


@pytest.mark.asyncio
async def test_row_to_anime_stats_with_none_rating(query):
    """Test del helper _row_to_anime_stats con rating None."""
    row = {
        "anime_id": 1,
        "total_clicks": 50,
        "total_views": 100,
        "total_ratings": 0,
        "average_rating": None,
        "total_duration_seconds": 3600
    }
    result = query._row_to_anime_stats(row)
    assert result.average_rating is None


@pytest.mark.asyncio
async def test_row_to_anime(query):
    """Test del helper _row_to_anime."""
    row = {
        "myanimelist_id": 1,
        "title": "Test Anime",
        "description": "Test description",
        "image": "test.jpg",
        "type": "TV",
        "episodes": 12,
        "score": 8.5,
        "popularity": 100
    }
    result = query._row_to_anime(row)
    assert result.myanimelist_id == 1
    assert result.title == "Test Anime"
    assert result.description == "Test description"
    assert result.image == "test.jpg"
    assert result.type == "TV"
    assert result.episodes == 12
    assert result.score == 8.5
    assert result.popularity == 100