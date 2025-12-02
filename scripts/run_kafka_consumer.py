"""Script para ejecutar el consumidor de Kafka."""
import asyncio
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

