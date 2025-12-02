"""Productor de Kafka para eventos."""
import json
from typing import List
from kafka import KafkaProducer
from common.events.base_event import BaseEvent
from config.settings import settings


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

