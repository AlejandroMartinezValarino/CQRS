#!/bin/bash
set -e

echo "=========================================="
echo "Iniciando Command Side API"
echo "=========================================="

# Esperar a que PostgreSQL esté disponible
echo "Esperando a que PostgreSQL esté disponible..."
if ! python scripts/wait_for_postgres.py; then
    echo "ERROR: PostgreSQL no está disponible después de esperar"
    echo "Continuando de todas formas (las migraciones pueden fallar)..."
fi

echo ""
echo "Creando bases de datos si no existen..."
if ! python scripts/create_databases.py; then
    echo "ERROR: Falló la creación de bases de datos"
    exit 1
fi

echo "Ejecutando migraciones..."
if ! python scripts/run_migrations.py; then
    echo "ERROR: Fallaron las migraciones"
    exit 1
fi

PORT=${PORT:-8000}
echo "=========================================="
echo "Iniciando Command Side API en puerto $PORT..."
echo "=========================================="
exec python -m uvicorn app.command_side.api.main:app --host 0.0.0.0 --port $PORT --workers 4
