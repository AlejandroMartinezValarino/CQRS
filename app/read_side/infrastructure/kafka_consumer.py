"""Consumidor de Kafka para procesar eventos."""
import json
from aiokafka import AIOKafkaConsumer
from app.read_side.projections.event_processor import EventProcessor
from config.settings import settings


class KafkaEventConsumer:
    """Consumidor de eventos desde Kafka."""
    
    def __init__(self):
        self.consumer: AIOKafkaConsumer = None
        self.event_processor = EventProcessor()
    
    async def start(self):
        """Inicia el consumidor."""
        await self.event_processor.connect()
        
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_EVENTS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="read-side-consumer-group",
        )
        
        await self.consumer.start()
    
    async def stop(self):
        """Detiene el consumidor."""
        if self.consumer:
            await self.consumer.stop()
        await self.event_processor.close()
    
    async def consume_events(self):
        """Consume eventos de Kafka y los procesa."""
        async for message in self.consumer:
            event = message.value
            event_type = event.get("event_type")
            
            try:
                if event_type == "ClickRegistered":
                    await self.event_processor.process_click_event(event)
                elif event_type == "ViewRegistered":
                    await self.event_processor.process_view_event(event)
                elif event_type == "RatingGiven":
                    await self.event_processor.process_rating_event(event)
            except Exception as e:
                # En producción, deberías loguear esto y posiblemente enviarlo a un DLQ
                print(f"Error procesando evento {event_type}: {e}")

