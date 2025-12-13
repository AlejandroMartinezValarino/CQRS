"""Aplicación GraphQL principal con configuración para producción."""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from common.utils.logger import get_logger
from app.read_side.graphql.schema import schema, get_repository
from config.settings import settings

logger = get_logger(__name__)

app = FastAPI(
    title="CQRS Read Side GraphQL",
    version="1.0.0",
    description="GraphQL API para consultas del sistema CQRS",
    docs_url="/graphql/docs" if not settings.is_production else None,
)

if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.on_event("startup")
async def startup():
    """Inicialización al arrancar."""
    logger.info("Iniciando Read Side GraphQL API...")
    try:
        repo = get_repository()
        await repo.connect()
        logger.info("Read Side GraphQL API iniciada correctamente")
    except Exception as e:
        logger.critical(f"Error al iniciar Read Side GraphQL API: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown():
    """Limpieza al cerrar."""
    logger.info("Cerrando Read Side GraphQL API...")
    try:
        repo = get_repository()
        await repo.close()
        logger.info("Read Side GraphQL API cerrada correctamente")
    except Exception as e:
        logger.error(f"Error al cerrar Read Side GraphQL API: {e}", exc_info=True)


@app.get("/health")
async def health():
    """Endpoint de salud con verificación de dependencias."""
    health_status = {
        "status": "healthy",
        "service": "read-side-graphql",
        "version": "1.0.0"
    }
    
    try:
        repo = get_repository()
        # Verificar solo conectividad, no hacer query pesada
        if repo._pool and not repo._pool._closed:
            health_status["dependencies"] = {
                "database": "healthy"
            }
        else:
            raise Exception("Pool not connected")
    except Exception as e:
        logger.warning(f"Health check falló: {e}")
        health_status["status"] = "degraded"
        health_status["dependencies"] = {
            "database": "unhealthy"
        }
        # Retornar 200 en lugar de 503 para que Railway no marque el servicio como caído
    
    return health_status

@app.get("/metrics")
async def metrics():
    """Endpoint de métricas del sistema."""
    repo = get_repository()
    cache_stats = repo.get_cache_stats()
    
    metrics_data = {
        "service": "read-side-graphql",
        "version": "1.0.0",
        "cache": cache_stats if cache_stats else {"enabled": False}
    }
    
    return metrics_data

@app.get("/ready")
async def readiness():
    """Endpoint de readiness (Kubernetes)."""
    try:
        repo = get_repository()
        await repo.get_anime_stats(1)  # Query de prueba
        return {"status": "ready"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready"}
        )


@app.get("/live")
async def liveness():
    """Endpoint de liveness (Kubernetes)."""
    return {"status": "alive"}

