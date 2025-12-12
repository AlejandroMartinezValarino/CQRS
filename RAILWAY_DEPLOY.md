# Despliegue en Railway

Este proyecto está configurado para desplegarse en Railway con 3 servicios separados.

## Servicios

1. **Command Side API** - FastAPI en puerto 8000
2. **Read Side GraphQL** - GraphQL API en puerto 8001
3. **Kafka Consumer** - Procesador de eventos en background

## Configuración en Railway

### 1. Crear los servicios

En Railway, crea 3 servicios separados desde el mismo repositorio:

- **Service 1 (Command)**: Usa `Dockerfile.command`
- **Service 2 (Read)**: Usa `Dockerfile.read`
- **Service 3 (Consumer)**: Usa `Dockerfile.consumer`

### 2. Variables de Entorno

Configura estas variables de entorno en cada servicio (o globalmente):

**PostgreSQL:**
```
POSTGRES_HOST=<railway-postgres-host>
POSTGRES_PORT=5432
POSTGRES_USER=<railway-postgres-user>
POSTGRES_PASSWORD=<railway-postgres-password>
POSTGRES_DB=cqrs_db
POSTGRES_EVENT_STORE_DB=cqrs_event_store
```

**Kafka:**
```
KAFKA_BOOTSTRAP_SERVERS=<kafka-broker-url>
KAFKA_TOPIC_EVENTS=anime-events
```

**Aplicación:**
```
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Nota:** Railway asigna automáticamente la variable `PORT` a cada servicio.

### 3. Base de Datos

Railway proporciona PostgreSQL. Necesitas crear dos bases de datos:
- `cqrs_db` - Para el read model
- `cqrs_event_store` - Para el event store

Las migraciones se ejecutan automáticamente al iniciar cada servicio.

### 4. Kafka

Railway no proporciona Kafka nativamente. Opciones:
- Usar un servicio externo (Confluent Cloud, Upstash, etc.)
- Usar Railway Kafka si está disponible
- Configurar Kafka como servicio separado

## Estructura de Archivos

- `Dockerfile.command` - Imagen para Command Side
- `Dockerfile.read` - Imagen para Read Side
- `Dockerfile.consumer` - Imagen para Kafka Consumer
- `scripts/start_command.sh` - Script de inicio para Command Side
- `scripts/start_read.sh` - Script de inicio para Read Side
- `scripts/start_consumer.sh` - Script de inicio para Consumer
- `scripts/run_migrations.py` - Ejecuta migraciones usando asyncpg
- `railway.json` - Configuración de Railway (opcional)
- `Procfile` - Definición de procesos (opcional)

## Notas

- Las migraciones se ejecutan automáticamente al iniciar cada servicio
- Cada servicio tiene su propio puerto asignado por Railway
- El consumer espera a que PostgreSQL esté disponible antes de iniciar

## Desarrollo Local con Docker Compose

Para desarrollo local, puedes usar `docker-compose.yml`:

```bash
docker-compose up
```

Esto iniciará:
- PostgreSQL (puerto 5432)
- Kafka + Zookeeper (puerto 9092)
- Command Side API (puerto 8000)
- Read Side GraphQL (puerto 8001)
- Kafka Consumer

**Nota:** Railway NO usa docker-compose. Cada servicio se despliega individualmente usando su Dockerfile correspondiente.
