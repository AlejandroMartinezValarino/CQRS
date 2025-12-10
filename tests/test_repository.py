"""Tests para ReadModelRepository."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.read_side.infrastructure.repository import ReadModelRepository
from config.settings import settings


@pytest.fixture
def repository():
    """Fixture para ReadModelRepository."""
    return ReadModelRepository()


@pytest.fixture
def mock_pool():
    """Fixture para mock del pool."""
    pool = MagicMock()
    conn = AsyncMock()
    
    context = AsyncMock()
    context.__aenter__ = AsyncMock(return_value=conn)
    context.__aexit__ = AsyncMock(return_value=None)
    pool.acquire = MagicMock(return_value=context)
    
    return pool, conn


@pytest.mark.asyncio
async def test_connect_success(repository):
    """Test que connect() crea el pool correctamente."""
    with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_create_pool:
        mock_pool = MagicMock()
        mock_create_pool.return_value = mock_pool
        await repository.connect()
        mock_create_pool.assert_called_once_with(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            min_size=settings.POSTGRES_MIN_CONNECTIONS,
            max_size=settings.POSTGRES_MAX_CONNECTIONS,
            command_timeout=settings.POSTGRES_COMMAND_TIMEOUT,
        )
        assert repository._pool is not None
        assert repository._pool == mock_pool


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, 101]) 
async def test_get_top_animes_by_views_invalid_limit(repository, mock_pool, limit):
    """Test que get_top_animes_by_views valida el límite."""
    pool, conn = mock_pool
    repository._pool = pool
    with pytest.raises(ValueError):
        await repository.get_top_animes_by_views(limit)


@pytest.mark.asyncio
async def test_get_top_animes_by_views_not_connected(repository):
    """Test que get_top_animes_by_views lanza error si no está conectado."""
    with pytest.raises(RuntimeError):
        await repository.get_top_animes_by_views(10)


@pytest.mark.asyncio
async def test_get_top_animes_by_views_success(repository, mock_pool):
    """Test que get_top_animes_by_views retorna resultados correctos."""
    pool, conn = mock_pool
    repository._pool = pool
    conn.fetch = AsyncMock(return_value=[{"anime_id": 1, "total_views": 100}])
    results = await repository.get_top_animes_by_views(10)
    assert len(results) == 1
    assert results[0]["anime_id"] == 1
    assert results[0]["total_views"] == 100

@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, 101]) 
async def test_get_top_animes_by_rating_invalid_limit(repository, mock_pool, limit):
    """Test que get_top_animes_by_rating valida el límite."""
    pool, conn = mock_pool
    repository._pool = pool
    with pytest.raises(ValueError):
        await repository.get_top_animes_by_rating(limit)

@pytest.mark.asyncio
async def test_get_top_animes_by_rating_not_connected(repository):
    """Test que get_top_animes_by_rating lanza error si no está conectado."""
    with pytest.raises(RuntimeError):
        await repository.get_top_animes_by_rating(10)   

@pytest.mark.asyncio
async def test_get_top_animes_by_rating_success(repository, mock_pool):
    """Test que get_top_animes_by_rating retorna resultados correctos."""
    pool, conn = mock_pool
    repository._pool = pool
    conn.fetch = AsyncMock(return_value=[{"anime_id": 1, "average_rating": 100}])
    results = await repository.get_top_animes_by_rating(10)
    assert len(results) == 1
    assert results[0]["anime_id"] == 1
    assert results[0]["average_rating"] == 100

@pytest.mark.asyncio
async def test_get_anime_stats_invalid_id(repository, mock_pool):
    """Test que get_anime_stats valida el anime_id."""
    pool, conn = mock_pool
    repository._pool = pool
    with pytest.raises(ValueError):
        await repository.get_anime_stats(0)


@pytest.mark.asyncio
async def test_get_anime_stats_not_connected(repository):
    """Test que get_anime_stats lanza error si no está conectado."""
    with pytest.raises(RuntimeError):
        await repository.get_anime_stats(1)


@pytest.mark.asyncio
async def test_get_anime_stats_not_found(repository, mock_pool):
    """Test que get_anime_stats retorna None cuando no encuentra el anime."""
    pool, conn = mock_pool
    repository._pool = pool
    conn.fetchrow = AsyncMock(return_value=None)
    result = await repository.get_anime_stats(1)
    assert result is None


@pytest.mark.asyncio
async def test_get_anime_stats_success(repository, mock_pool):
    """Test que get_anime_stats retorna resultados correctos."""
    pool, conn = mock_pool
    repository._pool = pool
    conn.fetchrow = AsyncMock(return_value={"anime_id": 1, "total_views": 100})
    result = await repository.get_anime_stats(1)
    assert result["anime_id"] == 1
    assert result["total_views"] == 100


@pytest.mark.asyncio
async def test_get_anime_invalid_id(repository, mock_pool):
    """Test que get_anime valida el anime_id."""
    pool, conn = mock_pool
    repository._pool = pool
    with pytest.raises(ValueError):
        await repository.get_anime(0)


@pytest.mark.asyncio
async def test_get_anime_not_connected(repository):
    """Test que get_anime lanza error si no está conectado."""
    with pytest.raises(RuntimeError):
        await repository.get_anime(1)


@pytest.mark.asyncio
async def test_get_anime_not_found(repository, mock_pool):
    """Test que get_anime retorna None cuando no encuentra el anime."""
    pool, conn = mock_pool
    repository._pool = pool
    conn.fetchrow = AsyncMock(return_value=None)
    result = await repository.get_anime(1)
    assert result is None


@pytest.mark.asyncio
async def test_get_anime_success(repository, mock_pool):
    """Test que get_anime retorna resultados correctos."""
    pool, conn = mock_pool
    repository._pool = pool
    conn.fetchrow = AsyncMock(return_value={"anime_id": 1, "total_views": 100})
    result = await repository.get_anime(1)
    assert result["anime_id"] == 1
    assert result["total_views"] == 100


@pytest.mark.asyncio
async def test_close_success(repository, mock_pool):
    """Test que close() cierra el pool correctamente."""
    pool, conn = mock_pool
    repository._pool = pool
    pool.close = AsyncMock()
    await repository.close()
    pool.close.assert_called_once()


@pytest.mark.asyncio
async def test_close_no_pool(repository):
    """Test que close() no falla si no hay pool."""
    await repository.close()
    assert repository._pool is None