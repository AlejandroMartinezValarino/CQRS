#!/bin/bash
set -e

echo "Ejecutando migraciones..."
python scripts/run_migrations.py || echo "Advertencia: Las migraciones pueden haber fallado o ya estar aplicadas"

PORT=${PORT:-8000}
echo "Iniciando Command Side API en puerto $PORT..."
exec python -m uvicorn app.command_side.api.main:app --host 0.0.0.0 --port $PORT --workers 4
