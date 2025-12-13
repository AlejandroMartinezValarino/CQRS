# Diagnóstico de conexión PostgreSQL en Railway

## Problema actual
Los servicios `command-side` y `read-side` no pueden conectarse a PostgreSQL usando hostnames internos (`postgres.railway.internal` o `postgres`).

## Pasos para diagnosticar

### 1. Verificar variables de entorno disponibles
En el terminal de Railway (desde la consola web), ejecuta:
```bash
python scripts/check_env.py
```

Esto mostrará qué variables están disponibles:
- `RAILWAY_PRIVATE_DOMAIN` - hostname privado del servicio PostgreSQL
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD` - credenciales de PostgreSQL
- `DATABASE_URL` - URL completa de conexión

### 2. Verificar si `RAILWAY_PRIVATE_DOMAIN` está disponible

Si `check_env.py` muestra que `RAILWAY_PRIVATE_DOMAIN` **NO está disponible**, tienes dos opciones:

#### Opción A: Configurar `DATABASE_URL` manualmente (recomendada)
En Railway, para los servicios `command-side` y `read-side`, configura:
```
DATABASE_URL=postgresql://postgres:CJkRNiDCPwIaGQnbUxbWiGvUETVabAXo@postgres.railway.internal:5432/cqrs_db
```

Según la imagen que compartiste, el hostname correcto aparece como `postgres.railway.internal`. Usa ese hostname directamente en lugar del template `${{RAILWAY_PRIVATE_DOMAIN}}`.

#### Opción B: Verificar la red privada
Asegúrate de que:
1. Los servicios `command-side`, `read-side` y `Postgres` están en el **mismo proyecto** de Railway
2. La red privada está habilitada en el proyecto
3. Los servicios han sido desplegados después de conectar el PostgreSQL

### 3. Verificar el hostname correcto
Según la documentación de Railway y tu captura de pantalla, el hostname puede ser:
- `postgres.railway.internal` (FQDN completo) - mostrado en tu imagen
- `postgres` (nombre corto) - mencionado en la documentación

### 4. Solución temporal: usar variables individuales
Si `RAILWAY_PRIVATE_DOMAIN` no está disponible, configura manualmente en Railway:
```
POSTGRES_HOST=postgres.railway.internal
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CJkRNiDCPwIaGQnbUxbWiGvUETVabAXo
POSTGRES_DB=cqrs_db
```

Y elimina o deja vacío `DATABASE_URL` (o pon un valor que no empiece con `${{`).

## Problema identificado

Railway proporciona `RAILWAY_PRIVATE_DOMAIN` como variable de entorno **en el servicio PostgreSQL**, pero no necesariamente la expone a los servicios que **consumen** PostgreSQL.

Los servicios consumidores reciben:
- `DATABASE_URL` (con templates `${{...}}` que Railway debería resolver)
- Variables `PGHOST`, `PGPORT`, etc. (con templates que Railway debería resolver)

Si Railway no está resolviendo estos templates automáticamente, necesitas configurar los valores manualmente.

## Próximos pasos después del diagnóstico

1. Ejecuta `python scripts/check_env.py` en Railway
2. Comparte el output
3. Según los resultados, ajustaremos la configuración
