# Troubleshooting Error 502 en Railway

## Síntomas
- Los servicios se inician correctamente en los logs
- Los dominios devuelven error 502: "Application failed to respond"

## Causas posibles

### 1. Puerto incorrecto
Railway espera que la aplicación escuche en el puerto especificado por la variable de entorno `PORT` (que Railway establece como 8080 por defecto).

**Verificar en los logs:**
```
Iniciando Command Side API en puerto 8080...
INFO:     Uvicorn running on http://0.0.0.0:8080
```

**Verificar en Railway:**
- Ve a Settings del servicio → Variables
- Asegúrate de que NO estés sobrescribiendo `PORT`
- Railway automáticamente asigna `PORT=8080` y redirige el tráfico

**Si ves esto en tus variables:**
```
API_PORT=8000  ❌ INCORRECTO
GRAPHQL_PORT=8001  ❌ INCORRECTO
```

**Solución:**
Elimina `API_PORT` y `GRAPHQL_PORT` de las variables de Railway, o asegúrate de que los scripts usen `PORT` en su lugar.

### 2. Configuración de dominios incorrecta

**Verificar:**
1. Ve a Settings del servicio → Networking → Domains
2. Cada dominio debe apuntar al servicio correcto:
   - `cqrs-api.alejandrotech.eu` → servicio `COMMAND` (o como se llame)
   - `cqrs-graphql.alejandrotech.eu` → servicio `READ` (o como se llame)

### 3. Health check path

Railway hace health checks automáticos. Si tu aplicación no responde en el path raíz `/`, puede marcarla como no saludable.

**Verificar en los logs si hay requests de health check:**
```
GET / 404 Not Found
GET /health 404 Not Found
```

**Solución:**
Agregar endpoints de health check en ambas APIs.

### 4. El servicio se cae después de iniciar

**Verificar:**
- Mira los logs después de "Application startup complete"
- Busca errores de conexión a base de datos
- Busca excepciones no capturadas

### 5. Dominios apuntando al puerto público incorrecto

Railway NO usa los puertos internos (8000, 8001) para dominios externos. Usa el puerto que la aplicación reporta vía `PORT`.

**En start_command.sh y start_read.sh:**
```bash
PORT=${PORT:-8000}  # Usa el PORT de Railway o 8000 por defecto
exec python -m uvicorn ... --port $PORT
```

Esto debería usar `PORT=8080` que Railway asigna automáticamente.

## Pasos para diagnosticar

1. **Ver logs en tiempo real:**
   - Railway Dashboard → Service → Logs
   - Busca "Iniciando Command Side API en puerto..."
   - Verifica que use puerto 8080

2. **Verificar health desde dentro del contenedor:**
   En Railway terminal:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/
   ```

3. **Verificar configuración de variables:**
   ```bash
   python scripts/check_env.py | grep PORT
   ```

4. **Ver los últimos logs:**
   - Busca errores después de "Application startup complete"
   - Busca "Connection refused" o "Address already in use"

## Solución rápida

Si el problema es el puerto, verifica que tu `start_command.sh` y `start_read.sh` usen correctamente la variable `PORT`:

```bash
# Debe usar $PORT, no $API_PORT
PORT=${PORT:-8000}
exec python -m uvicorn app.command_side.api.main:app --host 0.0.0.0 --port $PORT --workers 4
```

Railway establece `PORT=8080` y espera que la app escuche ahí. Los dominios externos se enrutan automáticamente a ese puerto.
