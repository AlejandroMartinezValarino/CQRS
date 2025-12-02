"""Configuración de logging profesional."""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config.settings import settings


def setup_logging():
    """Configura el sistema de logging."""
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Formato de logs
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO if settings.is_production else logging.DEBUG)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo (rotación)
    file_handler = RotatingFileHandler(
        log_dir / "application.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(file_handler)
    
    # Handler para errores (archivo separado)
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_handler.setFormatter(log_format)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    
    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("kafka").setLevel(logging.WARNING)
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre especificado."""
    return logging.getLogger(name)


# Configurar logging al importar el módulo
setup_logging()

