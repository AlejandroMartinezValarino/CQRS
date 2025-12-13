"""Productor de Kafka para eventos."""
import json
from typing import List
from kafka import KafkaProducer
from kafka.errors import KafkaError
from common.events.base_event import BaseEvent
from common.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class KafkaEventProducer:
    """Productor de eventos a Kafka."""
    
    def __init__(self):
        self._producer: KafkaProducer = None
    
    def connect(self):
        """Conecta al broker de Kafka."""
        self._producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
    
    def publish_events(self, events: List[BaseEvent]):
        """Publica eventos a Kafka."""
        if not self._producer:
            self.connect()
        
        for event in events:
            self._producer.send(
                settings.KAFKA_TOPIC_EVENTS,
                key=event.aggregate_id,
                value=event.model_dump(),
            )
        
        self._producer.flush()
    
    def close(self):
        """Cierra el productor."""
        if self._producer:
            self._producer.close()
    
    def health_check(self) -> bool:
        """Verifica la salud de la conexión a Kafka."""
        try:
            if not self._producer:
                self.connect()
            
            # Verificar que el productor esté inicializado y tenga conexión
            # bootstrap_connected() verifica si hay al menos un broker conectado
            if hasattr(self._producer, '_metadata'):
                # El productor está inicializado correctamente
                return True
            return self._producer is not None
        except (KafkaError, Exception) as e:
            logger.error(f"Health check de Kafka falló: {e}")
            return False

