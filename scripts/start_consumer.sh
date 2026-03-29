#!/bin/bash
set -e

echo "Esperando a que la base de datos esté lista..."
until python scripts/check_db.py; do
  echo "Esperando PostgreSQL..."
  sleep 2
done

echo "Migraciones del read model (processed_events, DLQ, índices)..."
python scripts/run_migrations.py || echo "Advertencia: revisar migraciones"

echo "Iniciando Kafka Consumer..."
exec python scripts/run_kafka_consumer.py
