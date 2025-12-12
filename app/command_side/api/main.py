"""API principal de FastAPI (Command Side) con configuración para producción."""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from common.dto.command_dto import ClickCommand, ViewCommand, RatingCommand
from common.utils.logger import get_logger
from app.command_side.application.anime_command_handler import AnimeCommandHandler
from config.settings import settings
from common.exceptions import AnimeNotFoundError, InvalidRatingError, DomainException


logger = get_logger(__name__)

app = FastAPI(
    title="CQRS Command Side API",
    version="1.0.0",
    description="API para comandos del sistema CQRS",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

command_handler = AnimeCommandHandler()


@app.on_event("startup")
async def startup():
    """Inicialización al arrancar."""
    logger.info("Iniciando Command Side API...")
    try:
        await command_handler.initialize()
        logger.info("Command Side API iniciada correctamente")
    except Exception as e:
        logger.critical(f"Error al iniciar Command Side API: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown():
    """Limpieza al cerrar."""
    logger.info("Cerrando Command Side API...")
    try:
        await command_handler.cleanup()
        logger.info("Command Side API cerrada correctamente")
    except Exception as e:
        logger.error(f"Error al cerrar Command Side API: {e}", exc_info=True)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones."""
    logger.error(f"Excepción no manejada: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Error interno del servidor" if settings.is_production else str(exc)
        }
    )


@app.post("/click", status_code=status.HTTP_201_CREATED)
async def register_click(command: ClickCommand):
    """Registra un click en un anime."""
    try:
        logger.info(f"Registrando click: anime_id={command.anime_id}, user_id={command.user_id}")
        await command_handler.handle_click(command)
        return {"status": "ok", "message": "Click registrado"}
    except AnimeNotFoundError as e:
        logger.warning(f"Anime no encontrado: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DomainException as e:
        logger.warning(f"Error de dominio en click: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error registrando click: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar click" if settings.is_production else str(e)
        )

@app.post("/view", status_code=status.HTTP_201_CREATED)
async def register_view(command: ViewCommand):
    """Registra una visualización de un anime."""
    try:
        logger.info(
            f"Registrando view: anime_id={command.anime_id}, user_id={command.user_id}, "
            f"duration={command.duration_seconds}s"
        )
        await command_handler.handle_view(command)
        return {"status": "ok", "message": "Visualización registrada"}
    except AnimeNotFoundError as e:
        logger.warning(f"Anime no encontrado: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DomainException as e:
        logger.warning(f"Error de dominio en view: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error registrando view: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar visualización" if settings.is_production else str(e)
        )


@app.post("/rating", status_code=status.HTTP_201_CREATED)
async def register_rating(command: RatingCommand):
    """Registra una calificación de un anime."""
    try:
        logger.info(
            f"Registrando rating: anime_id={command.anime_id}, user_id={command.user_id}, "
            f"rating={command.rating}"
        )
        await command_handler.handle_rating(command)
        return {"status": "ok", "message": "Calificación registrada"}
    except AnimeNotFoundError as e:
        logger.warning(f"Anime no encontrado: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidRatingError as e:
        logger.warning(f"Calificación inválida: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DomainException as e:
        logger.warning(f"Error de dominio en rating: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error registrando rating: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar calificación" if settings.is_production else str(e)
        )


@app.get("/health")
async def health():
    """Endpoint de salud con verificación de dependencias."""
    health_status = {
        "status": "healthy",
        "service": "command-side-api",
        "version": "1.0.0"
    }
    
    event_store_healthy = await command_handler.event_store.health_check()
    kafka_healthy = command_handler.kafka_producer.health_check()
    health_status["dependencies"] = {
        "event_store": "healthy" if event_store_healthy else "unhealthy",
        "kafka": "healthy" if kafka_healthy else "unhealthy"
    }
    
    if not event_store_healthy or not kafka_healthy:
        health_status["status"] = "degraded"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status


@app.get("/ready")
async def readiness():
    """Endpoint de readiness (Kubernetes)."""
    event_store_healthy = await command_handler.event_store.health_check()
    if not event_store_healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready"}
        )
    return {"status": "ready"}


@app.get("/live")
async def liveness():
    """Endpoint de liveness (Kubernetes)."""
    return {"status": "alive"}

