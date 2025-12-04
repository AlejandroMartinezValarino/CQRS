import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from common.dto.command_dto import ClickCommand, ViewCommand, RatingCommand
from common.exceptions import AnimeNotFoundError, InvalidRatingError
from app.command_side.application.anime_command_handler import AnimeCommandHandler
from pydantic import ValidationError


@pytest.fixture
def mock_event_store():
    """Fixture para EventStore mock."""
    store = MagicMock()
    store.connect = AsyncMock()
    store.close = AsyncMock()
    store.save_events = AsyncMock()
    return store


@pytest.fixture
def mock_kafka_producer():
    """Fixture para KafkaEventProducer mock."""
    producer = MagicMock()
    producer.connect = MagicMock()
    producer.close = MagicMock()
    producer.publish_events = MagicMock()
    return producer


@pytest.fixture
def mock_anime_validator():
    """Fixture para AnimeValidator mock."""
    validator = MagicMock()
    validator.anime_exists = AsyncMock(return_value=True)
    validator.close = AsyncMock()
    return validator


@pytest.fixture
def handler(mock_event_store, mock_kafka_producer, mock_anime_validator):
    """Fixture para AnimeCommandHandler con mocks."""
    with patch('app.command_side.application.anime_command_handler.EventStore', return_value=mock_event_store), \
         patch('app.command_side.application.anime_command_handler.KafkaEventProducer', return_value=mock_kafka_producer), \
         patch('app.command_side.application.anime_command_handler.AnimeValidator', return_value=mock_anime_validator):
        handler = AnimeCommandHandler()
        return handler


@pytest.mark.asyncio
async def test_handle_click_success(handler, mock_anime_validator, mock_event_store, mock_kafka_producer):
    """Test que handle_click funciona correctamente cuando el anime existe."""
    command = ClickCommand(anime_id=1, user_id="user123")
    mock_anime_validator.anime_exists.return_value = True
    
    await handler.handle_click(command)
    
    mock_anime_validator.anime_exists.assert_called_once_with(1)
    
    mock_event_store.save_events.assert_called_once()
    saved_events = mock_event_store.save_events.call_args[0][0]
    assert len(saved_events) == 1
    assert saved_events[0].anime_id == 1
    assert saved_events[0].user_id == "user123"
    
    mock_kafka_producer.publish_events.assert_called_once()


@pytest.mark.asyncio
async def test_handle_click_anime_not_found(handler, mock_anime_validator):
    """Test que handle_click lanza excepción cuando el anime no existe."""
    command = ClickCommand(anime_id=999, user_id="user123")
    mock_anime_validator.anime_exists.return_value = False
    
    with pytest.raises(AnimeNotFoundError) as exc_info:
        await handler.handle_click(command)
    
    assert exc_info.value.anime_id == 999
    mock_anime_validator.anime_exists.assert_called_once_with(999)


@pytest.mark.asyncio
async def test_handle_view_success(handler, mock_anime_validator, mock_event_store, mock_kafka_producer):
    """Test que handle_view funciona correctamente cuando el anime existe."""
    command = ViewCommand(anime_id=1, user_id="user123", duration_seconds=3600)
    mock_anime_validator.anime_exists.return_value = True
    
    await handler.handle_view(command)
    
    mock_anime_validator.anime_exists.assert_called_once_with(1)
    
    mock_event_store.save_events.assert_called_once()
    saved_events = mock_event_store.save_events.call_args[0][0]
    assert len(saved_events) == 1
    assert saved_events[0].anime_id == 1
    assert saved_events[0].duration_seconds == 3600
    
    mock_kafka_producer.publish_events.assert_called_once()


@pytest.mark.asyncio
async def test_handle_view_anime_not_found(handler, mock_anime_validator):
    """Test que handle_view lanza excepción cuando el anime no existe."""
    command = ViewCommand(anime_id=999, user_id="user123", duration_seconds=3600)
    mock_anime_validator.anime_exists.return_value = False
    
    with pytest.raises(AnimeNotFoundError) as exc_info:
        await handler.handle_view(command)
    
    assert exc_info.value.anime_id == 999


@pytest.mark.asyncio
async def test_handle_rating_success(handler, mock_anime_validator, mock_event_store, mock_kafka_producer):
    """Test que handle_rating funciona correctamente con rating válido."""
    command = RatingCommand(anime_id=1, user_id="user123", rating=8.5)
    mock_anime_validator.anime_exists.return_value = True
    
    await handler.handle_rating(command)
    
    mock_anime_validator.anime_exists.assert_called_once_with(1)
    
    mock_event_store.save_events.assert_called_once()
    saved_events = mock_event_store.save_events.call_args[0][0]
    assert len(saved_events) == 1
    assert saved_events[0].rating == 8.5
    
    mock_kafka_producer.publish_events.assert_called_once()


@pytest.mark.asyncio
async def test_handle_rating_anime_not_found(handler, mock_anime_validator):
    """Test que handle_rating lanza excepción cuando el anime no existe."""
    command = RatingCommand(anime_id=999, user_id="user123", rating=8.5)
    mock_anime_validator.anime_exists.return_value = False
    
    with pytest.raises(AnimeNotFoundError) as exc_info:
        await handler.handle_rating(command)
    
    assert exc_info.value.anime_id == 999


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_rating", [0.5, 0.0])
async def test_handle_rating_invalid_rating_low(handler, mock_anime_validator, invalid_rating):
    """Test que handle_rating lanza excepción con ratings muy bajos."""
    command = RatingCommand.model_construct(anime_id=1, user_id="user123", rating=invalid_rating)
    mock_anime_validator.anime_exists.return_value = True
    
    with pytest.raises(InvalidRatingError) as exc_info:
        await handler.handle_rating(command)
    
    assert exc_info.value.rating == invalid_rating


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_rating", [10.1, 11.0, 15.0])
async def test_handle_rating_invalid_rating_high(handler, mock_anime_validator, invalid_rating):
    """Test que Pydantic rechaza ratings muy altos antes del handler."""
    
    with pytest.raises(ValidationError):
        RatingCommand(anime_id=1, user_id="user123", rating=invalid_rating)


@pytest.mark.asyncio
@pytest.mark.parametrize("valid_rating", [1.0, 5.0, 7.5, 10.0])
async def test_handle_rating_valid_boundaries(handler, mock_anime_validator, mock_event_store, valid_rating):
    """Test que handle_rating acepta ratings en los límites válidos."""
    command = RatingCommand(anime_id=1, user_id="user123", rating=valid_rating)
    mock_anime_validator.anime_exists.return_value = True
    
    await handler.handle_rating(command)
    
    mock_event_store.save_events.assert_called_once()


@pytest.mark.asyncio
async def test_initialize(handler, mock_event_store, mock_kafka_producer):
    """Test que initialize() inicializa correctamente los componentes."""
    await handler.initialize()
    
    mock_event_store.connect.assert_called_once()
    mock_kafka_producer.connect.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup(handler, mock_event_store, mock_kafka_producer, mock_anime_validator):
    """Test que cleanup() cierra correctamente los componentes."""
    await handler.cleanup()
    
    mock_event_store.close.assert_called_once()
    mock_kafka_producer.close.assert_called_once()
    mock_anime_validator.close.assert_called_once()