"""Manejador de comandos de anime con logging y manejo de errores."""
from datetime import datetime
from common.dto.command_dto import ClickCommand, ViewCommand, RatingCommand
from common.events.anime_events import ClickRegistered, ViewRegistered, RatingGiven
from common.utils.logger import get_logger
from app.command_side.infrastructure.event_store import EventStore
from app.command_side.infrastructure.kafka_producer import KafkaEventProducer

logger = get_logger(__name__)


class AnimeCommandHandler:
    """Manejador de comandos relacionados con animes."""
    
    def __init__(self):
        self.event_store = EventStore()
        self.kafka_producer = KafkaEventProducer()
    
    async def initialize(self):
        """Inicializa las conexiones."""
        logger.info("Inicializando AnimeCommandHandler...")
        try:
            await self.event_store.connect()
            self.kafka_producer.connect()
            logger.info("AnimeCommandHandler inicializado correctamente")
        except Exception as e:
            logger.critical(f"Error al inicializar AnimeCommandHandler: {e}", exc_info=True)
            raise
    
    async def cleanup(self):
        """Limpia las conexiones."""
        logger.info("Cerrando AnimeCommandHandler...")
        try:
            await self.event_store.close()
            self.kafka_producer.close()
            logger.info("AnimeCommandHandler cerrado correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar AnimeCommandHandler: {e}", exc_info=True)
    
    async def handle_click(self, command: ClickCommand):
        """Maneja el comando de click."""
        event = ClickRegistered(
            aggregate_id=f"anime_{command.anime_id}",
            anime_id=command.anime_id,
            user_id=command.user_id,
            timestamp=datetime.utcnow(),
        )
        
        # Guardar en Event Store
        await self.event_store.save_events([event])
        
        # Publicar a Kafka
        self.kafka_producer.publish_events([event])
    
    async def handle_view(self, command: ViewCommand):
        """Maneja el comando de visualización."""
        event = ViewRegistered(
            aggregate_id=f"anime_{command.anime_id}",
            anime_id=command.anime_id,
            user_id=command.user_id,
            duration_seconds=command.duration_seconds,
            timestamp=datetime.utcnow(),
        )
        
        # Guardar en Event Store
        await self.event_store.save_events([event])
        
        # Publicar a Kafka
        self.kafka_producer.publish_events([event])
    
    async def handle_rating(self, command: RatingCommand):
        """Maneja el comando de calificación."""
        event = RatingGiven(
            aggregate_id=f"anime_{command.anime_id}",
            anime_id=command.anime_id,
            user_id=command.user_id,
            rating=command.rating,
            timestamp=datetime.utcnow(),
        )
        
        # Guardar en Event Store
        await self.event_store.save_events([event])
        
        # Publicar a Kafka
        self.kafka_producer.publish_events([event])

