"""Consumidor de Kafka para procesar eventos."""
import json
import asyncio
from typing import Optional
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from app.read_side.projections.event_processor import EventProcessor, EventProcessingError
from app.read_side.infrastructure.dlq_handler import DLQHandler
from common.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class KafkaEventConsumer:
    """Consumidor de eventos desde Kafka con manejo robusto de errores."""
    
    def __init__(self):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.event_processor = EventProcessor()
        self.dlq_handler = DLQHandler()
        self._running = False
        self._processed_count = 0
        self._error_count = 0
    
    async def start(self):
        """Inicia el consumidor."""
        try:
            logger.info("Iniciando KafkaEventConsumer...")
            await self.event_processor.connect()
            await self.dlq_handler.connect()
            
            self.consumer = AIOKafkaConsumer(
                settings.KAFKA_TOPIC_EVENTS,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                group_id="read-side-consumer-group",
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                max_poll_records=10,
            )
            
            await self.consumer.start()
            self._running = True
            logger.info(
                f"KafkaEventConsumer iniciado correctamente. "
                f"Topic: {settings.KAFKA_TOPIC_EVENTS}, "
                f"Servers: {settings.KAFKA_BOOTSTRAP_SERVERS}"
            )
        except Exception as e:
            logger.error(f"Error iniciando KafkaEventConsumer: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """Detiene el consumidor."""
        try:
            logger.info("Deteniendo KafkaEventConsumer...")
            self._running = False
            
            if self.consumer:
                await self.consumer.stop()
                logger.info("Consumidor de Kafka detenido")
            
            await self.event_processor.close()
            await self.dlq_handler.close()
            logger.info(
                f"KafkaEventConsumer detenido. "
                f"Eventos procesados: {self._processed_count}, "
                f"Errores: {self._error_count}"
            )
        except Exception as e:
            logger.error(f"Error deteniendo KafkaEventConsumer: {e}", exc_info=True)
    
    async def consume_events(self):
        """Consume eventos de Kafka y los procesa."""
        if not self._running:
            logger.warning("Consumidor no está corriendo, no se pueden consumir eventos")
            return
        
        logger.info("Iniciando consumo de eventos de Kafka...")
        
        try:
            async for message in self.consumer:
                if not self._running:
                    logger.info("Consumidor detenido, saliendo del loop")
                    break
                
                try:
                    await self._process_message(message)
                    self._processed_count += 1
                except Exception as e:
                    self._error_count += 1
                    await self._handle_message_error(message, e)
                
        except KafkaError as e:
            logger.error(f"Error de Kafka: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error inesperado en consume_events: {e}", exc_info=True)
            raise
    
    async def _process_message(self, message):
        """Procesa un mensaje individual."""
        event = message.value
        event_type = event.get("event_type")
        event_id = event.get("event_id", "unknown")
        
        logger.debug(f"Procesando evento: type={event_type}, id={event_id}")
        
        try:
            if event_type == "ClickRegistered":
                await self.event_processor.process_click_event(event)
            elif event_type == "ViewRegistered":
                await self.event_processor.process_view_event(event)
            elif event_type == "RatingGiven":
                await self.event_processor.process_rating_event(event)
            else:
                logger.warning(f"Tipo de evento desconocido: {event_type}, evento_id={event_id}")
        except EventProcessingError as e:
            logger.error(
                f"Error procesando evento {event_type} (id={event_id}): {e}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Error inesperado procesando evento {event_type} (id={event_id}): {e}",
                exc_info=True
            )
            raise
    
    async def _handle_message_error(self, message, error: Exception):
        """Maneja errores al procesar un mensaje enviándolo a la DLQ."""
        event = message.value
        event_type = event.get("event_type", "unknown")
        event_id = event.get("event_id", "unknown")
        
        logger.error(
            f"EVENTO FALLIDO - type={event_type}, id={event_id}, "
            f"error={type(error).__name__}: {str(error)}, "
            f"topic={message.topic}, partition={message.partition}, offset={message.offset}",
            exc_info=True
        )
        
        try:
            await self.dlq_handler.store_failed_event(event, error, message.topic, message.partition, message.offset)
        except Exception as dlq_error:
            logger.critical(f"Error crítico almacenando en DLQ: {dlq_error}. Evento original perdido: {event_id}", exc_info=True)
    
    async def health_check(self) -> dict:
        """Verifica la salud del consumidor."""
        return {
            "status": "healthy" if self._running else "stopped",
            "processed_events": self._processed_count,
            "error_count": self._error_count,
            "consumer_running": self._running and self.consumer is not None,
        }