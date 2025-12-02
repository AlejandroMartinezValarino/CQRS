# 🎯 Sistema CQRS con Event Sourcing

Sistema completo de arquitectura CQRS (Command Query Responsibility Segregation) con Event Sourcing, implementado en Python. Este proyecto demuestra el dominio de patrones arquitectónicos avanzados, microservicios, y tecnologías modernas.

## 🏗️ Arquitectura

El proyecto implementa una arquitectura CQRS completa con separación clara entre comandos (escritura) y consultas (lectura):

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   FastAPI   │────────▶│   Event      │────────▶│   Kafka     │
│  (Commands) │         │   Store      │         │  (Events)   │
└─────────────┘         └──────────────┘         └─────────────┘
                                                       │
                                                       ▼
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  GraphQL    │◀────────│   Read       │◀────────│  Consumer   │
│  (Queries)  │         │   Model      │         │  (Projections)│
└─────────────┘         └──────────────┘         └─────────────┘
```

### Componentes Principales

- **Command Side (FastAPI)**: API REST para recibir comandos de escritura
- **Read Side (GraphQL)**: API GraphQL optimizada para consultas
- **Event Store (PostgreSQL)**: Almacenamiento inmutable de eventos
- **Event Bus (Kafka)**: Sistema de mensajería para eventos
- **Projections**: Procesamiento asíncrono de eventos para read models

## 🚀 Tecnologías y Patrones

### Stack Tecnológico
- **Python 3.10+** - Lenguaje principal
- **FastAPI** - Framework web moderno y rápido
- **Strawberry GraphQL** - GraphQL type-safe
- **PostgreSQL** - Base de datos relacional
- **Kafka** - Sistema de mensajería distribuida
- **Pydantic** - Validación de datos y configuración
- **AsyncPG** - Driver asíncrono para PostgreSQL

### Patrones Arquitectónicos
- ✅ **CQRS** - Separación de comandos y consultas
- ✅ **Event Sourcing** - Almacenamiento basado en eventos
- ✅ **Domain-Driven Design (DDD)** - Organización por capas de dominio
- ✅ **Event-Driven Architecture** - Comunicación mediante eventos
- ✅ **Repository Pattern** - Abstracción de acceso a datos
- ✅ **Command Handler Pattern** - Procesamiento de comandos

## 📁 Estructura del Proyecto

```
CQRS/
├── app/
│   ├── command_side/          # Lado de comandos (escritura)
│   │   ├── api/               # Endpoints FastAPI
│   │   ├── application/       # Handlers de comandos
│   │   ├── domain/            # Agregados y lógica de dominio
│   │   └── infrastructure/    # Event Store, Kafka Producer
│   └── read_side/             # Lado de consultas (lectura)
│       ├── graphql/           # Schema y resolvers GraphQL
│       ├── projections/       # Procesadores de eventos
│       └── infrastructure/    # Kafka Consumer, Repository
├── common/
│   ├── events/                # Eventos del dominio
│   ├── dto/                   # Data Transfer Objects
│   └── utils/                 # Utilidades (logging, retry)
├── config/                    # Configuración centralizada
└── scripts/                   # Scripts de utilidad
```

## ✨ Características Destacadas

### 🎯 Arquitectura Profesional
- Separación clara de responsabilidades (CQRS)
- Event Sourcing completo con Event Store
- Proyecciones asíncronas para read models
- Diseño escalable y mantenible

### 🔒 Calidad y Robustez
- **Logging profesional**: Sistema de logs con rotación y niveles configurables
- **Manejo de errores**: Retry logic con exponential backoff
- **Health checks**: Endpoints `/health`, `/ready`, `/live` para monitoreo
- **Validación**: Configuración robusta con Pydantic Settings
- **Connection pooling**: Optimización de conexiones a base de datos

### 📊 Caso de Uso: Sistema de Analytics para Animes
El proyecto implementa un sistema de tracking de interacciones de usuarios con animes:
- **Clicks**: Registro de clicks en animes
- **Views**: Seguimiento de visualizaciones con duración
- **Ratings**: Sistema de calificaciones

Los eventos se procesan asíncronamente para generar estadísticas agregadas consultables vía GraphQL.

## 🛠️ Instalación y Uso

### Requisitos Previos
- Python 3.10+
- PostgreSQL 12+
- Kafka 2.8+

### Instalación Rápida

```bash
# 1. Clonar y entrar al directorio
cd CQRS

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Crear bases de datos
createdb cqrs_db
createdb cqrs_event_store

# 6. Ejecutar migraciones
python scripts/run_migrations.py

# 7. Cargar datos de ejemplo
python scripts/load_mal_to_postgres.py
```

### Ejecutar el Sistema

**Terminal 1 - Command Side:**
```bash
uvicorn app.command_side.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Read Side:**
```bash
uvicorn app.read_side.graphql.main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 3 - Kafka Consumer:**
```bash
python scripts/run_kafka_consumer.py
```

## 📡 API Endpoints

### Command Side (FastAPI)
- `POST /click` - Registrar un click en un anime
- `POST /view` - Registrar una visualización
- `POST /rating` - Registrar una calificación
- `GET /health` - Health check con verificación de dependencias

### Read Side (GraphQL)
- `POST /graphql` - Endpoint GraphQL
- `GET /health` - Health check

### Ejemplo de Uso

**Registrar un evento:**
```bash
curl -X POST http://localhost:8000/click \
  -H "Content-Type: application/json" \
  -d '{"anime_id": 1, "user_id": "user123"}'
```

**Consultar estadísticas:**
```graphql
query {
  topAnimesByViews(limit: 10) {
    animeId
    totalViews
    totalClicks
    averageRating
  }
}
```

## 🎓 Conceptos Demostrados

Este proyecto demuestra conocimiento y experiencia en:

1. **Arquitectura de Software**
   - CQRS y Event Sourcing
   - Domain-Driven Design
   - Event-Driven Architecture
   - Microservicios

2. **Patrones de Diseño**
   - Repository Pattern
   - Command Handler
   - Event Sourcing
   - CQRS

3. **Tecnologías Modernas**
   - FastAPI y async/await
   - GraphQL con Strawberry
   - Kafka para mensajería
   - PostgreSQL avanzado

4. **Buenas Prácticas**
   - Logging estructurado
   - Manejo de errores robusto
   - Configuración centralizada
   - Health checks y monitoreo

## 📈 Escalabilidad

El sistema está diseñado para escalar:
- **Command Side**: Puede escalar horizontalmente (stateless)
- **Read Side**: Optimizado para consultas con read models
- **Event Processing**: Procesamiento asíncrono con Kafka
- **Database**: Connection pooling y optimización de queries

## 🔧 Configuración

El proyecto usa configuración basada en variables de entorno con validación:

```python
# config/settings.py
class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    POSTGRES_HOST: str = "localhost"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    # ... más configuración
```

## 📝 Notas Técnicas

- Los eventos se almacenan de forma inmutable en el Event Store
- Las proyecciones se actualizan asíncronamente desde Kafka
- El sistema soporta replay de eventos para reconstruir read models
- Health checks verifican la conectividad con todas las dependencias

## 🎯 Objetivo del Proyecto

Este proyecto fue desarrollado para demostrar:
- Comprensión profunda de arquitecturas complejas
- Capacidad de implementar patrones avanzados
- Experiencia con tecnologías modernas
- Buenas prácticas de desarrollo

---

**Desarrollado con ❤️ usando Python, FastAPI, GraphQL, Kafka y PostgreSQL**
