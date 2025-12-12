"""Tests de integración para Event Store."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from app.command_side.infrastructure.event_store import EventStore
from common.events.anime_events import ClickRegistered, ViewRegistered, RatingGiven
from config.settings import settings


@pytest.fixture
def event_store():
    """Fixture para EventStore."""
    return EventStore()


@pytest.fixture
def mock_pool():
    """Fixture para mock del pool de conexiones."""
    pool = MagicMock()
    conn = AsyncMock()
    
    context = AsyncMock()
    context.__aenter__ = AsyncMock(return_value=conn)
    context.__aexit__ = AsyncMock(return_value=None)
    pool.acquire = MagicMock(return_value=context)
    pool.is_closing = MagicMock(return_value=False)
    
    return pool, conn


@pytest.mark.asyncio
async def test_connect_success(event_store):
    """Test que connect() crea el pool correctamente."""
    with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_create_pool:
        mock_pool = MagicMock()
        mock_pool.is_closing = MagicMock(return_value=False)
        mock_create_pool.return_value = mock_pool
        
        await event_store.connect()
        
        mock_create_pool.assert_called_once()
        assert event_store._pool == mock_pool
        assert event_store._connected is True


@pytest.mark.asyncio
async def test_connect_already_connected(event_store, mock_pool):
    """Test que connect() no crea un nuevo pool si ya existe."""
    pool, conn = mock_pool
    event_store._pool = pool
    
    with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_create_pool:
        await event_store.connect()
        mock_create_pool.assert_not_called()


@pytest.mark.asyncio
async def test_save_events_success(event_store, mock_pool):
    """Test que save_events() guarda eventos correctamente."""
    pool, conn = mock_pool
    event_store._pool = pool
    
    click_event = ClickRegistered(
        aggregate_id="anime_1",
        anime_id=1,
        user_id="user123"
    )
    view_event = ViewRegistered(
        aggregate_id="anime_1",
        anime_id=1,
        user_id="user123",
        duration_seconds=300
    )
    events = [click_event, view_event]
    
    transaction = MagicMock()
    transaction.__aenter__ = AsyncMock(return_value=transaction)
    transaction.__aexit__ = AsyncMock(return_value=None)
    conn.transaction = MagicMock(return_value=transaction)
    conn.execute = AsyncMock()
    
    await event_store.save_events(events)
    
    assert conn.execute.call_count == 2
    conn.transaction.assert_called_once()


@pytest.mark.asyncio
async def test_save_events_empty_list(event_store, mock_pool):
    """Test que save_events() no hace nada con lista vacía."""
    pool, conn = mock_pool
    event_store._pool = pool
    
    await event_store.save_events([])
    
    assert not hasattr(conn, 'execute') or conn.execute.call_count == 0


@pytest.mark.asyncio
async def test_save_events_auto_connect(event_store):
    """Test que save_events() conecta automáticamente si no hay pool."""
    with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock_create_pool:
        mock_pool = MagicMock()
        conn = AsyncMock()
        
        context = AsyncMock()
        context.__aenter__ = AsyncMock(return_value=conn)
        context.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire = MagicMock(return_value=context)
        mock_pool.is_closing = MagicMock(return_value=False)
        
        transaction = MagicMock()
        transaction.__aenter__ = AsyncMock(return_value=transaction)
        transaction.__aexit__ = AsyncMock(return_value=None)
        conn.transaction = MagicMock(return_value=transaction)
        conn.execute = AsyncMock()
        
        mock_create_pool.return_value = mock_pool
        
        click_event = ClickRegistered(
            aggregate_id="anime_1",
            anime_id=1,
            user_id="user123"
        )
        
        await event_store.save_events([click_event])
        
        mock_create_pool.assert_called_once()
        conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_health_check_success(event_store, mock_pool):
    """Test que health_check() retorna True cuando está saludable."""
    pool, conn = mock_pool
    event_store._pool = pool
    conn.fetchval = AsyncMock(return_value=1)
    
    result = await event_store.health_check()
    
    assert result is True
    conn.fetchval.assert_called_once_with("SELECT 1")


@pytest.mark.asyncio
async def test_health_check_no_pool(event_store):
    """Test que health_check() retorna False cuando no hay pool."""
    result = await event_store.health_check()
    assert result is False


@pytest.mark.asyncio
async def test_health_check_pool_closing(event_store, mock_pool):
    """Test que health_check() retorna False cuando el pool está cerrando."""
    pool, conn = mock_pool
    pool.is_closing = MagicMock(return_value=True)
    event_store._pool = pool
    
    result = await event_store.health_check()
    assert result is False


@pytest.mark.asyncio
async def test_health_check_connection_error(event_store, mock_pool):
    """Test que health_check() retorna False cuando hay error de conexión."""
    pool, conn = mock_pool
    event_store._pool = pool
    conn.fetchval = AsyncMock(side_effect=Exception("Connection error"))
    
    result = await event_store.health_check()
    assert result is False


@pytest.mark.asyncio
async def test_get_events_by_aggregate_id_success(event_store, mock_pool):
    """Test que get_events_by_aggregate_id() retorna eventos correctamente."""
    pool, conn = mock_pool
    event_store._pool = pool
    
    mock_row1 = {"event_data": '{"event_type": "ClickRegistered", "anime_id": 1}'}
    mock_row2 = {"event_data": '{"event_type": "ViewRegistered", "anime_id": 1}'}
    conn.fetch = AsyncMock(return_value=[mock_row1, mock_row2])
    
    events = await event_store.get_events_by_aggregate_id("anime_1")
    
    assert len(events) == 2
    conn.fetch.assert_called_once()
    call_args = conn.fetch.call_args[0]
    assert "aggregate_id" in call_args[0] or "$1" in call_args[0]


@pytest.mark.asyncio
async def test_get_events_by_aggregate_id_with_version(event_store, mock_pool):
    """Test que get_events_by_aggregate_id() filtra por versión."""
    pool, conn = mock_pool
    event_store._pool = pool
    
    conn.fetch = AsyncMock(return_value=[])
    
    events = await event_store.get_events_by_aggregate_id("anime_1", from_version=5)
    
    assert len(events) == 0
    conn.fetch.assert_called_once()


@pytest.mark.asyncio
async def test_close_success(event_store, mock_pool):
    """Test que close() cierra el pool correctamente."""
    pool, conn = mock_pool
    event_store._pool = pool
    event_store._connected = True
    pool.close = AsyncMock()
    
    await event_store.close()
    
    pool.close.assert_called_once()
    assert event_store._connected is False


@pytest.mark.asyncio
async def test_close_no_pool(event_store):
    """Test que close() no falla si no hay pool."""
    await event_store.close()
    assert event_store._pool is None

