"""Tests para KafkaEventConsumer."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.read_side.infrastructure import dlq_handler
from app.read_side.infrastructure.kafka_consumer import KafkaEventConsumer


@pytest.fixture
def kafka_consumer():
    """Fixture para KafkaEventConsumer."""
    return KafkaEventConsumer()


@pytest.fixture
def mock_kafka_message():
    """Fixture para mock de mensaje de Kafka."""
    message = MagicMock()
    message.value = {
        "event_id": "test-123",
        "event_type": "ClickRegistered",
        "aggregate_id": "anime_1",
        "anime_id": 1,
        "user_id": "user123",
        "occurred_at": datetime.utcnow()
    }
    message.topic = "anime-events"
    message.partition = 0
    message.offset = 12345
    return message


@pytest.mark.asyncio
async def test_start_success(kafka_consumer):
    """Test que start() inicializa correctamente los componentes."""
    kafka_consumer.event_processor = MagicMock()
    kafka_consumer.event_processor.connect = AsyncMock()
    kafka_consumer.dlq_handler = MagicMock()
    kafka_consumer.dlq_handler.connect = AsyncMock()
    
    mock_consumer = AsyncMock()
    mock_consumer.start = AsyncMock()
    
    with patch('app.read_side.infrastructure.kafka_consumer.AIOKafkaConsumer', return_value=mock_consumer):
        await kafka_consumer.start()
    
    kafka_consumer.event_processor.connect.assert_called_once()
    kafka_consumer.dlq_handler.connect.assert_called_once()
    mock_consumer.start.assert_called_once()
    assert kafka_consumer._running is True
    assert kafka_consumer.consumer == mock_consumer


@pytest.mark.asyncio
async def test_stop_success(kafka_consumer):
    """Test que stop() cierra correctamente los componentes."""
    kafka_consumer.consumer = AsyncMock()
    kafka_consumer.consumer.stop = AsyncMock()
    kafka_consumer.event_processor = MagicMock()
    kafka_consumer.event_processor.close = AsyncMock()
    kafka_consumer.dlq_handler = MagicMock()
    kafka_consumer.dlq_handler.close = AsyncMock()
    kafka_consumer._running = True
    
    await kafka_consumer.stop()

    assert kafka_consumer._running is False

    kafka_consumer.consumer.stop.assert_called_once()
    kafka_consumer.event_processor.close.assert_called_once()
    kafka_consumer.dlq_handler.close.assert_called_once()
    


@pytest.mark.asyncio
async def test_process_message_click_registered(kafka_consumer, mock_kafka_message):
    """Test que _process_message procesa correctamente ClickRegistered."""
    kafka_consumer.event_processor = MagicMock()
    kafka_consumer.event_processor.process_click_event = AsyncMock()
    
    await kafka_consumer._process_message(mock_kafka_message)

    kafka_consumer.event_processor.process_click_event.assert_called_once_with(mock_kafka_message.value)
    

@pytest.mark.asyncio
async def test_process_message_view_registered(kafka_consumer):
    """Test que _process_message procesa correctamente ViewRegistered."""
    kafka_consumer.event_processor = MagicMock()
    kafka_consumer.event_processor.process_view_event = AsyncMock()
    
    message = MagicMock()
    message.value = {
        "event_id": "view-123",
        "event_type": "ViewRegistered",
        "anime_id": 1,
        "user_id": "user123",
        "duration_seconds": 3600,
        "occurred_at": datetime.utcnow()
    }
    
    await kafka_consumer._process_message(message)

    kafka_consumer.event_processor.process_view_event.assert_called_once_with(message.value)


@pytest.mark.asyncio
async def test_process_message_unknown_event_type(kafka_consumer):
    """Test que _process_message loguea warning para eventos desconocidos."""
    kafka_consumer.event_processor = MagicMock()
    
    message = MagicMock()
    message.value = {
        "event_id": "unknown-123",
        "event_type": "UnknownEvent",
    }
        
    await kafka_consumer._process_message(message)
    
    kafka_consumer.event_processor.process_click_event.assert_not_called()
    kafka_consumer.event_processor.process_view_event.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_error_stores_in_dlq(kafka_consumer, mock_kafka_message):
    """Test que _handle_message_error almacena el evento en DLQ."""
    kafka_consumer.dlq_handler = MagicMock()
    kafka_consumer.dlq_handler.store_failed_event = AsyncMock(return_value=1)
    
    error = Exception("Test error")
    
    await kafka_consumer._handle_message_error(mock_kafka_message, error)

    kafka_consumer.dlq_handler.store_failed_event.assert_called_once_with(mock_kafka_message.value, error, "anime-events", 0, 12345)
    


@pytest.mark.asyncio
async def test_handle_message_error_dlq_failure(kafka_consumer, mock_kafka_message):
    """Test que _handle_message_error maneja fallos del DLQ gracefully."""
    kafka_consumer.dlq_handler = MagicMock()
    kafka_consumer.dlq_handler.store_failed_event = AsyncMock(side_effect=Exception("DLQ error"))
    
    error = Exception("Original error")
    
    await kafka_consumer._handle_message_error(mock_kafka_message, error)

    kafka_consumer.dlq_handler.store_failed_event.assert_called_once_with(mock_kafka_message.value, error, "anime-events", 0, 12345)
    


@pytest.mark.asyncio
async def test_consume_events_increments_counters(kafka_consumer):
    """Test que consume_events incrementa contadores correctamente."""
    kafka_consumer._running = True
    kafka_consumer.consumer = AsyncMock()
    
    message1 = MagicMock()
    message1.value = {
        "event_id": "event-1",
        "event_type": "ClickRegistered",
        "anime_id": 1,
        "user_id": "user1",
        "occurred_at": datetime.utcnow()
    }
    
    message2 = MagicMock()
    message2.value = {
        "event_id": "event-2",
        "event_type": "ViewRegistered",
        "anime_id": 1,
        "user_id": "user1",
        "duration_seconds": 100,
        "occurred_at": datetime.utcnow()
    }
    
    async def mock_consume():
        yield message1
        yield message2
        kafka_consumer._running = False 
    
    kafka_consumer.consumer.__aiter__ = lambda self: mock_consume()
    kafka_consumer._process_message = AsyncMock()
    
    kafka_consumer._processed_count = 0
    kafka_consumer._error_count = 0
    
    await kafka_consumer.consume_events()

    assert kafka_consumer._process_message.call_count == 2
    assert kafka_consumer._processed_count == 2
    assert kafka_consumer._error_count == 0


@pytest.mark.asyncio
async def test_health_check_healthy(kafka_consumer):
    """Test que health_check retorna estado correcto cuando está corriendo."""
    kafka_consumer._running = True
    kafka_consumer.consumer = MagicMock()
    kafka_consumer._processed_count = 10
    kafka_consumer._error_count = 2
    
    result = await kafka_consumer.health_check()

    assert result['status'] == "healthy"
    assert result['processed_events'] == 10
    assert result['error_count'] == 2
    assert result['consumer_running'] == True


