#!/bin/bash
set -e

echo "Creando bases de datos si no existen..."
python scripts/create_databases.py || echo "Advertencia: Error creando bases de datos"

echo "Ejecutando migraciones..."
python scripts/run_migrations.py || echo "Advertencia: Las migraciones pueden haber fallado o ya estar aplicadas"

PORT=${PORT:-8001}
echo "Iniciando Read Side GraphQL en puerto $PORT..."
exec python -m uvicorn app.read_side.graphql.main:app --host 0.0.0.0 --port $PORT --workers 4
