#!/bin/bash
set -e

echo "=========================================="
echo "Iniciando Command Side API"
echo "=========================================="

# Esperar a que la red privada esté lista (según Railway docs)
# Algunos usuarios reportan que necesitan más tiempo
echo "Esperando a que la red privada esté lista..."
sleep 5

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
