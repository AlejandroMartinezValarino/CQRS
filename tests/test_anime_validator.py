import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.command_side.domain.anime_validator import AnimeValidator


@pytest.mark.asyncio
async def test_anime_exists_true():
    """Test que anime_exists retorna True cuando el anime existe."""
    validator = AnimeValidator()
    
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=True)
    
    mock_pool = MagicMock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_pool.acquire = MagicMock(return_value=mock_context)
    
    with patch('app.command_side.domain.anime_validator.asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
        mock_create_pool.return_value = mock_pool
        
        result = await validator.anime_exists(anime_id=1)
        
        assert result is True
        mock_conn.fetchval.assert_called_once_with(
            "SELECT EXISTS(SELECT 1 FROM animes WHERE myanimelist_id = $1)",
            1
        )


@pytest.mark.asyncio
async def test_anime_exists_false():
    """Test que anime_exists retorna False cuando el anime no existe."""
    validator = AnimeValidator()
    
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=False)
    
    mock_pool = MagicMock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_pool.acquire = MagicMock(return_value=mock_context)
    
    with patch('app.command_side.domain.anime_validator.asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
        mock_create_pool.return_value = mock_pool
        
        result = await validator.anime_exists(anime_id=999)
        
        assert result is False
        mock_conn.fetchval.assert_called_once_with(
            "SELECT EXISTS(SELECT 1 FROM animes WHERE myanimelist_id = $1)",
            999
        )


@pytest.mark.asyncio
async def test_anime_validator_pool_reuse():
    """Test que el pool se reutiliza en múltiples llamadas."""
    validator = AnimeValidator()
    
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=True)
    
    mock_pool = MagicMock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_pool.acquire = MagicMock(return_value=mock_context)
    
    with patch('app.command_side.domain.anime_validator.asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
        mock_create_pool.return_value = mock_pool
        
        await validator.anime_exists(anime_id=1)
        
        await validator.anime_exists(anime_id=2)
        
        assert mock_create_pool.call_count == 1


@pytest.mark.asyncio
async def test_anime_validator_close():
    """Test que close() cierra el pool correctamente."""
    validator = AnimeValidator()
    
    mock_pool = AsyncMock()
    mock_pool.close = AsyncMock()
    
    validator._pool = mock_pool
    
    await validator.close()
    
    mock_pool.close.assert_called_once()


@pytest.mark.asyncio
async def test_anime_validator_close_no_pool():
    """Test que close() no falla si no hay pool."""
    validator = AnimeValidator()
    
    await validator.close()
    assert validator._pool is None