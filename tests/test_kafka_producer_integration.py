"""Tests de integración para Kafka Producer."""
import pytest
from unittest.mock import MagicMock, patch, call
from app.command_side.infrastructure.kafka_producer import KafkaEventProducer
from common.events.anime_events import ClickRegistered, ViewRegistered, RatingGiven
from kafka.errors import KafkaError


@pytest.fixture
def kafka_producer():
    """Fixture para KafkaEventProducer."""
    return KafkaEventProducer()


@pytest.fixture
def mock_kafka_producer():
    """Fixture para mock de KafkaProducer."""
    producer = MagicMock()
    producer.send = MagicMock(return_value=MagicMock())
    producer.flush = MagicMock()
    producer.close = MagicMock()
    producer.list_topics = MagicMock(return_value=MagicMock())
    return producer


@pytest.mark.asyncio
async def test_connect_success(kafka_producer, mock_kafka_producer):
    """Test que connect() crea el producer correctamente."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer) as mock_kafka:
        kafka_producer.connect()
        
        mock_kafka.assert_called_once()
        assert kafka_producer._producer == mock_kafka_producer


@pytest.mark.asyncio
async def test_publish_events_success(kafka_producer, mock_kafka_producer):
    """Test que publish_events() publica eventos correctamente."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer):
        kafka_producer.connect()
        
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
        
        kafka_producer.publish_events(events)
        
        assert mock_kafka_producer.send.call_count == 2
        mock_kafka_producer.flush.assert_called_once()


@pytest.mark.asyncio
async def test_publish_events_auto_connect(kafka_producer, mock_kafka_producer):
    """Test que publish_events() conecta automáticamente si no hay producer."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer) as mock_kafka:
        click_event = ClickRegistered(
            aggregate_id="anime_1",
            anime_id=1,
            user_id="user123"
        )
        
        kafka_producer.publish_events([click_event])
        
        mock_kafka.assert_called_once()
        mock_kafka_producer.send.assert_called_once()
        mock_kafka_producer.flush.assert_called_once()


@pytest.mark.asyncio
async def test_publish_events_serialization(kafka_producer, mock_kafka_producer):
    """Test que publish_events() serializa eventos correctamente."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer):
        kafka_producer.connect()
        
        click_event = ClickRegistered(
            aggregate_id="anime_1",
            anime_id=1,
            user_id="user123"
        )
        
        kafka_producer.publish_events([click_event])
        
        send_call = mock_kafka_producer.send.call_args
        assert send_call is not None


@pytest.mark.asyncio
async def test_close_success(kafka_producer, mock_kafka_producer):
    """Test que close() cierra el producer correctamente."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer):
        kafka_producer.connect()
        kafka_producer.close()
        
        mock_kafka_producer.close.assert_called_once()


@pytest.mark.asyncio
async def test_close_no_producer(kafka_producer):
    """Test que close() no falla si no hay producer."""
    kafka_producer.close()
    assert kafka_producer._producer is None


@pytest.mark.asyncio
async def test_health_check_success(kafka_producer, mock_kafka_producer):
    """Test que health_check() retorna True cuando está saludable."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer):
        kafka_producer.connect()
        
        result = kafka_producer.health_check()
        
        assert result is True
        mock_kafka_producer.list_topics.assert_called_once_with(timeout=5)


@pytest.mark.asyncio
async def test_health_check_auto_connect(kafka_producer, mock_kafka_producer):
    """Test que health_check() conecta automáticamente si no hay producer."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer) as mock_kafka:
        result = kafka_producer.health_check()
        
        assert result is True
        mock_kafka.assert_called_once()
        mock_kafka_producer.list_topics.assert_called_once_with(timeout=5)


@pytest.mark.asyncio
async def test_health_check_kafka_error(kafka_producer, mock_kafka_producer):
    """Test que health_check() retorna False cuando hay error de Kafka."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer):
        kafka_producer.connect()
        mock_kafka_producer.list_topics.side_effect = KafkaError("Connection failed")
        
        result = kafka_producer.health_check()
        
        assert result is False


@pytest.mark.asyncio
async def test_health_check_general_exception(kafka_producer, mock_kafka_producer):
    """Test que health_check() retorna False cuando hay excepción general."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer):
        kafka_producer.connect()
        mock_kafka_producer.list_topics.side_effect = Exception("Unexpected error")
        
        result = kafka_producer.health_check()
        
        assert result is False


@pytest.mark.asyncio
async def test_publish_multiple_events_different_aggregates(kafka_producer, mock_kafka_producer):
    """Test que publish_events() maneja múltiples eventos de diferentes agregados."""
    with patch("app.command_side.infrastructure.kafka_producer.KafkaProducer", return_value=mock_kafka_producer):
        kafka_producer.connect()
        
        events = [
            ClickRegistered(aggregate_id="anime_1", anime_id=1, user_id="user1"),
            ClickRegistered(aggregate_id="anime_2", anime_id=2, user_id="user2"),
            ViewRegistered(aggregate_id="anime_1", anime_id=1, user_id="user1", duration_seconds=100),
        ]
        
        kafka_producer.publish_events(events)
        
        assert mock_kafka_producer.send.call_count == 3
        mock_kafka_producer.flush.assert_called_once()

