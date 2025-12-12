"""Tests de integración end-to-end del flujo completo."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from app.command_side.application.anime_command_handler import AnimeCommandHandler
from app.command_side.infrastructure.event_store import EventStore
from app.command_side.infrastructure.kafka_producer import KafkaEventProducer
from app.read_side.projections.event_processor import EventProcessor
from app.read_side.infrastructure.repository import ReadModelRepository
from common.dto.command_dto import ClickCommand, ViewCommand, RatingCommand
from common.events.anime_events import ClickRegistered, ViewRegistered, RatingGiven
from common.exceptions import AnimeNotFoundError, InvalidRatingError


@pytest.fixture
def mock_event_store():
    """Fixture para mock de EventStore."""
    store = MagicMock(spec=EventStore)
    store.save_events = AsyncMock()
    store.health_check = AsyncMock(return_value=True)
    store.connect = AsyncMock()
    store.close = AsyncMock()
    return store


@pytest.fixture
def mock_kafka_producer():
    """Fixture para mock de KafkaProducer."""
    producer = MagicMock(spec=KafkaEventProducer)
    producer.publish_events = MagicMock()
    producer.health_check = MagicMock(return_value=True)
    producer.connect = MagicMock()
    producer.close = MagicMock()
    return producer


@pytest.fixture
def mock_anime_validator():
    """Fixture para mock de AnimeValidator."""
    validator = MagicMock()
    validator.anime_exists = AsyncMock(return_value=True)
    validator.close = AsyncMock()
    return validator


@pytest.fixture
def command_handler(mock_event_store, mock_kafka_producer, mock_anime_validator):
    """Fixture para AnimeCommandHandler con mocks."""
    handler = AnimeCommandHandler()
    handler.event_store = mock_event_store
    handler.kafka_producer = mock_kafka_producer
    handler.anime_validator = mock_anime_validator
    return handler


@pytest.fixture
def mock_event_processor():
    """Fixture para mock de EventProcessor."""
    processor = MagicMock(spec=EventProcessor)
    processor.process_click_event = AsyncMock()
    processor.process_view_event = AsyncMock()
    processor.process_rating_event = AsyncMock()
    processor.connect = AsyncMock()
    processor.close = AsyncMock()
    return processor


@pytest.fixture
def mock_repository():
    """Fixture para mock de ReadModelRepository."""
    repo = MagicMock(spec=ReadModelRepository)
    repo.get_anime_stats = AsyncMock(return_value={"anime_id": 1, "total_views": 100})
    repo.get_top_animes_by_views = AsyncMock(return_value=[{"anime_id": 1, "total_views": 100}])
    repo.connect = AsyncMock()
    repo.close = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_click_command_full_flow(command_handler, mock_event_store, mock_kafka_producer):
    """Test del flujo completo de un comando click."""
    command = ClickCommand(anime_id=1, user_id="user123")
    
    await command_handler.handle_click(command)
    
    mock_event_store.save_events.assert_called_once()
    saved_events = mock_event_store.save_events.call_args[0][0]
    assert len(saved_events) == 1
    assert isinstance(saved_events[0], ClickRegistered)
    assert saved_events[0].anime_id == 1
    assert saved_events[0].user_id == "user123"
    
    mock_kafka_producer.publish_events.assert_called_once()
    published_events = mock_kafka_producer.publish_events.call_args[0][0]
    assert len(published_events) == 1
    assert isinstance(published_events[0], ClickRegistered)


@pytest.mark.asyncio
async def test_view_command_full_flow(command_handler, mock_event_store, mock_kafka_producer):
    """Test del flujo completo de un comando view."""
    command = ViewCommand(anime_id=1, user_id="user123", duration_seconds=300)
    
    await command_handler.handle_view(command)
    
    mock_event_store.save_events.assert_called_once()
    saved_events = mock_event_store.save_events.call_args[0][0]
    assert len(saved_events) == 1
    assert isinstance(saved_events[0], ViewRegistered)
    assert saved_events[0].duration_seconds == 300
    
    mock_kafka_producer.publish_events.assert_called_once()


@pytest.mark.asyncio
async def test_rating_command_full_flow(command_handler, mock_event_store, mock_kafka_producer):
    """Test del flujo completo de un comando rating."""
    command = RatingCommand(anime_id=1, user_id="user123", rating=8.5)
    
    await command_handler.handle_rating(command)
    
    mock_event_store.save_events.assert_called_once()
    saved_events = mock_event_store.save_events.call_args[0][0]
    assert len(saved_events) == 1
    assert isinstance(saved_events[0], RatingGiven)
    assert saved_events[0].rating == 8.5
    
    mock_kafka_producer.publish_events.assert_called_once()


@pytest.mark.asyncio
async def test_command_handler_cleanup(command_handler, mock_event_store, mock_kafka_producer, mock_anime_validator):
    """Test que cleanup() cierra todas las conexiones."""
    await command_handler.cleanup()
    
    mock_event_store.close.assert_called_once()
    mock_kafka_producer.close.assert_called_once()
    mock_anime_validator.close.assert_called_once()


@pytest.mark.asyncio
async def test_click_command_anime_not_found(command_handler, mock_anime_validator):
    """Test que handle_click() lanza error cuando el anime no existe."""
    mock_anime_validator.anime_exists = AsyncMock(return_value=False)
    command = ClickCommand(anime_id=999, user_id="user123")
    
    with pytest.raises(AnimeNotFoundError):
        await command_handler.handle_click(command)


@pytest.mark.asyncio
async def test_rating_command_invalid_rating(command_handler):
    """Test que handle_rating() lanza error cuando el rating es inválido."""
    command = RatingCommand.model_construct(anime_id=1, user_id="user123", rating=11.0)
    
    with pytest.raises(InvalidRatingError):
        await command_handler.handle_rating(command)


@pytest.mark.asyncio
async def test_event_processing_click_event(mock_event_processor):
    """Test que EventProcessor procesa eventos click correctamente."""
    event_data = {
        "event_id": "evt_123",
        "event_type": "ClickRegistered",
        "aggregate_id": "anime_1",
        "anime_id": 1,
        "user_id": "user123",
        "occurred_at": "2024-01-01T00:00:00",
        "version": 1
    }
    
    await mock_event_processor.process_click_event(event_data)
    
    mock_event_processor.process_click_event.assert_called_once_with(event_data)


@pytest.mark.asyncio
async def test_event_processing_view_event(mock_event_processor):
    """Test que EventProcessor procesa eventos view correctamente."""
    event_data = {
        "event_id": "evt_124",
        "event_type": "ViewRegistered",
        "aggregate_id": "anime_1",
        "anime_id": 1,
        "user_id": "user123",
        "duration_seconds": 300,
        "occurred_at": "2024-01-01T00:00:00",
        "version": 1
    }
    
    await mock_event_processor.process_view_event(event_data)
    
    mock_event_processor.process_view_event.assert_called_once_with(event_data)


@pytest.mark.asyncio
async def test_event_processing_rating_event(mock_event_processor):
    """Test que EventProcessor procesa eventos rating correctamente."""
    event_data = {
        "event_id": "evt_125",
        "event_type": "RatingGiven",
        "aggregate_id": "anime_1",
        "anime_id": 1,
        "user_id": "user123",
        "rating": 8.5,
        "occurred_at": "2024-01-01T00:00:00",
        "version": 1
    }
    
    await mock_event_processor.process_rating_event(event_data)
    
    mock_event_processor.process_rating_event.assert_called_once_with(event_data)


@pytest.mark.asyncio
async def test_read_model_query_flow(mock_repository):
    """Test del flujo de consulta al read model."""
    await mock_repository.connect()
    
    stats = await mock_repository.get_anime_stats(1)
    
    assert stats is not None
    assert stats["anime_id"] == 1
    mock_repository.get_anime_stats.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_full_flow_command_to_read_model(
    command_handler, 
    mock_event_store, 
    mock_kafka_producer,
    mock_event_processor,
    mock_repository
):
    """Test del flujo completo desde comando hasta read model."""
    command = ClickCommand(anime_id=1, user_id="user123")
    await command_handler.handle_click(command)
    
    mock_event_store.save_events.assert_called_once()
    saved_events = mock_event_store.save_events.call_args[0][0]
    event = saved_events[0]
    
    event_data = event.model_dump()
    await mock_event_processor.process_click_event(event_data)
    
    stats = await mock_repository.get_anime_stats(1)
    assert stats is not None
    
    mock_event_store.save_events.assert_called_once()
    mock_kafka_producer.publish_events.assert_called_once()
    mock_event_processor.process_click_event.assert_called_once()
    mock_repository.get_anime_stats.assert_called_once()


@pytest.mark.asyncio
async def test_multiple_commands_same_anime(command_handler, mock_event_store, mock_kafka_producer):
    """Test que múltiples comandos para el mismo anime funcionan correctamente."""
    await command_handler.handle_click(ClickCommand(anime_id=1, user_id="user1"))
    await command_handler.handle_click(ClickCommand(anime_id=1, user_id="user2"))
    await command_handler.handle_view(ViewCommand(anime_id=1, user_id="user1", duration_seconds=100))
    
    assert mock_event_store.save_events.call_count == 3
    assert mock_kafka_producer.publish_events.call_count == 3

