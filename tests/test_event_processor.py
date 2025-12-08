"""Tests para EventProcessor."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.read_side.projections.event_processor import EventProcessor, EventProcessingError
from config.settings import settings


@pytest.fixture
def event_processor():
    """Fixture para EventProcessor."""
    return EventProcessor()


@pytest.fixture
def mock_pool():
    """Fixture para mock del pool de conexiones."""
    pool = MagicMock()
    conn = AsyncMock()
    
    context = AsyncMock()
    context.__aenter__ = AsyncMock(return_value=conn)
    context.__aexit__ = AsyncMock(return_value=None)
    pool.acquire = MagicMock(return_value=context)
    
    return pool, conn


@pytest.mark.asyncio
async def test_connect_success(event_processor):
    """Test que connect() crea el pool correctamente."""

    mock_pool = MagicMock()

    with patch('app.read_side.projections.event_processor.asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
        mock_create_pool.return_value = mock_pool
        
        await event_processor.connect()
        
        mock_create_pool.assert_called_once_with(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            min_size=2,
            max_size=10,
        )
        assert event_processor._pool is not None
        assert event_processor._pool == mock_pool


@pytest.mark.asyncio
async def test_close_with_pool(event_processor, mock_pool):
    """Test que close() cierra el pool si existe."""
    pool, _ = mock_pool
    event_processor._pool = pool

    pool.close = AsyncMock()
    
    await event_processor.close()

    pool.close.assert_called_once()

    assert event_processor._pool is not None


@pytest.mark.asyncio
async def test_close_no_pool(event_processor):
    """Test que close() no falla si no hay pool."""
    event_processor._pool = None
    
    await event_processor.close()
    assert event_processor._pool is None


@pytest.mark.asyncio
async def test_is_event_processed_true(event_processor, mock_pool):
    """Test que _is_event_processed retorna True cuando el evento ya fue procesado."""
    pool, conn = mock_pool
    event_processor._pool = pool
    conn.fetchval = AsyncMock(return_value=True)
    
    result = await event_processor._is_event_processed("event-123")
    
    assert result is True

    conn.fetchval.assert_called_once_with(
        "SELECT EXISTS(SELECT 1 FROM processed_events WHERE event_id = $1 AND status = 'success')",
         "event-123")


@pytest.mark.asyncio
async def test_is_event_processed_false(event_processor, mock_pool):
    """Test que _is_event_processed retorna False cuando el evento no fue procesado."""
    pool, conn = mock_pool
    event_processor._pool = pool
    conn.fetchval = AsyncMock(return_value=False)
    
    result = await event_processor._is_event_processed("event-456")
    
    assert result is False


@pytest.mark.asyncio
async def test_mark_event_processed(event_processor, mock_pool):
    """Test que _mark_event_processed guarda el evento en processed_events."""
    pool, conn = mock_pool
    event_processor._pool = pool
    conn.execute = AsyncMock()
    
    await event_processor._mark_event_processed(
        event_id="event-123",
        event_type="ClickRegistered",
        aggregate_id="anime_1",
        duration_ms=50,
        status="success"
    )
    
    conn.execute.assert_called_once()

    call_args = conn.execute.call_args[0][0]
    assert "INSERT INTO processed_events" in call_args
    assert "event-123" in str(conn.execute.call_args[0])


@pytest.mark.asyncio
async def test_validate_event_success(event_processor):
    """Test que _validate_event no lanza excepción con campos válidos."""
    event = {
        "anime_id": 1,
        "user_id": "user123",
        "occurred_at": datetime.utcnow()
    }
    
    # No debería lanzar excepción
    event_processor._validate_event(event, ["anime_id", "user_id", "occurred_at"])


@pytest.mark.asyncio
async def test_validate_event_missing_fields(event_processor):
    """Test que _validate_event lanza excepción con campos faltantes."""
    event = {
        "anime_id": 1
        # Faltan user_id y occurred_at
    }
    
    with pytest.raises(EventProcessingError) as exc_info:
        event_processor._validate_event(event, ["anime_id", "user_id", "occurred_at"])
    
    assert "Evento inválido: faltan campos requeridos: ['user_id', 'occurred_at']" in str(exc_info.value)
    assert "user_id" in str(exc_info.value) or "occurred_at" in str(exc_info.value)

@pytest.mark.asyncio
async def test_process_click_event_success(event_processor, mock_pool):
    """Test que process_click_event procesa correctamente un evento de click."""
    pool, conn = mock_pool
    event_processor._pool = pool
    
    # Mock para _is_event_processed (retorna False = no procesado)
    event_processor._is_event_processed = AsyncMock(return_value=False)
    event_processor._mark_event_processed = AsyncMock()
    
    mock_transaction = AsyncMock()
    mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
    mock_transaction.__aexit__ = AsyncMock(return_value=None)
    conn.transaction = MagicMock(return_value=mock_transaction)
    
    conn.execute = AsyncMock()
    
    event = {
        "event_id": "click-123",
        "event_type": "ClickRegistered",
        "aggregate_id": "anime_1",
        "anime_id": 1,
        "user_id": "user123",
        "occurred_at": datetime.utcnow()
    }
    
    await event_processor.process_click_event(event)
    
    event_processor._is_event_processed.assert_called_once_with("click-123")
    assert conn.execute.call_count == 2
    event_processor._mark_event_processed.assert_called_once()

    call_args = event_processor._mark_event_processed.call_args
    assert call_args[0][4] == 'success'


@pytest.mark.asyncio
async def test_process_click_event_idempotency(event_processor):
    """Test que process_click_event no procesa eventos duplicados (idempotencia)."""
    event_processor._is_event_processed = AsyncMock(return_value=True)

    mock_pool = MagicMock()
    event_processor._pool = mock_pool
    
    event = {
        "event_id": "click-123",
        "event_type": "ClickRegistered",
        "aggregate_id": "anime_1",
        "anime_id": 1,
        "user_id": "user123",
        "occurred_at": datetime.utcnow()
    }
    
    await event_processor.process_click_event(event)
    
    event_processor._is_event_processed.assert_called_once_with("click-123")

@pytest.mark.asyncio
async def test_process_view_event_negative_duration(event_processor, mock_pool):
    """Test que process_view_event rechaza duration_seconds negativo."""
    pool, conn = mock_pool
    event_processor._pool = pool
    event_processor._is_event_processed = AsyncMock(return_value=False)
    event_processor._mark_event_processed = AsyncMock()
    
    event = {
        "event_id": "view-123",
        "event_type": "ViewRegistered",
        "aggregate_id": "anime_1",
        "anime_id": 1,
        "user_id": "user123",
        "duration_seconds": -10,  # Inválido
        "occurred_at": datetime.utcnow()
    }
    
    with pytest.raises(EventProcessingError) as exc_info:
        await event_processor.process_view_event(event)
    
    # Verificar el mensaje de error
    assert "duration_seconds debe ser positivo" in str(exc_info.value)


@pytest.mark.asyncio
async def test_process_rating_event_invalid_rating(event_processor, mock_pool):
    """Test que process_rating_event rechaza rating fuera de rango."""
    pool, conn = mock_pool
    event_processor._pool = pool
    event_processor._is_event_processed = AsyncMock(return_value=False)
    event_processor._mark_event_processed = AsyncMock()
    
    event = {
        "event_id": "rating-123",
        "event_type": "RatingGiven",
        "aggregate_id": "anime_1",
        "anime_id": 1,
        "user_id": "user123",
        "rating": 11.0,  # Inválido (debe ser 1.0-10.0)
        "occurred_at": datetime.utcnow()
    }
    
    with pytest.raises(EventProcessingError) as exc_info:
        await event_processor.process_rating_event(event)
    
    # Verificar el mensaje de error
    assert "Rating debe estar entre 1.0 y 10.0" in str(exc_info.value)

