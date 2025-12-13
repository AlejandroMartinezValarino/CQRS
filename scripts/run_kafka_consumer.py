"""Script para ejecutar el consumidor de Kafka."""
import asyncio
import sys
from pathlib import Path

# Añadir el directorio raíz al PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.read_side.infrastructure.kafka_consumer import KafkaEventConsumer


async def main():
    """Función principal."""
    consumer = KafkaEventConsumer()
    
    try:
        await consumer.start()
        print("Consumidor de Kafka iniciado. Presiona Ctrl+C para detener.")
        await consumer.consume_events()
    except KeyboardInterrupt:
        print("\nDeteniendo consumidor...")
    finally:
        await consumer.stop()
        print("Consumidor detenido.")


if __name__ == "__main__":
    asyncio.run(main())

