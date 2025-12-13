"""Utilidades para conexiones a base de datos."""
from typing import Dict, Any, Optional
from urllib.parse import urlparse, urlunparse
import asyncpg
from config.settings import settings


def get_pool_kwargs(
    database: Optional[str] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    command_timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Construye los parámetros para crear un pool de conexiones.
    
    Si DATABASE_URL está disponible, la usa y modifica la base de datos si se especifica.
    Si no, usa las variables individuales de configuración.
    
    Args:
        database: Nombre de la base de datos (opcional, sobrescribe la del DATABASE_URL)
        min_size: Tamaño mínimo del pool (opcional)
        max_size: Tamaño máximo del pool (opcional)
        command_timeout: Timeout de comandos (opcional)
    
    Returns:
        Diccionario con los parámetros para asyncpg.create_pool
    """
    kwargs: Dict[str, Any] = {}
    
    # Si DATABASE_URL está disponible y no es un template no resuelto, usarla
    if settings.DATABASE_URL and not settings.DATABASE_URL.startswith("${{"):
        try:
            # Parsear la URL (puede ser postgresql:// o postgres://)
            parsed = urlparse(settings.DATABASE_URL)
            
            # Si se especifica una base de datos diferente, modificar el path
            if database:
                # Construir nueva URL con la base de datos especificada
                new_path = f'/{database}'
                # Mantener query y fragment si existen
                new_parsed = parsed._replace(path=new_path)
                dsn = urlunparse(new_parsed)
            else:
                # Usar DATABASE_URL tal cual
                dsn = settings.DATABASE_URL
            
            kwargs['dsn'] = dsn
            
        except Exception:
            # Si hay error parseando DATABASE_URL, usar variables individuales
            pass
    
    # Si no se usó DATABASE_URL, usar variables individuales
    if 'dsn' not in kwargs:
        kwargs['host'] = settings.POSTGRES_HOST
        kwargs['port'] = settings.POSTGRES_PORT
        kwargs['user'] = settings.POSTGRES_USER
        kwargs['password'] = settings.POSTGRES_PASSWORD
        kwargs['database'] = database or settings.POSTGRES_DB
    
    # Agregar configuraciones del pool
    if min_size is not None:
        kwargs['min_size'] = min_size
    if max_size is not None:
        kwargs['max_size'] = max_size
    if command_timeout is not None:
        kwargs['command_timeout'] = command_timeout
    elif hasattr(settings, 'POSTGRES_COMMAND_TIMEOUT'):
        kwargs['command_timeout'] = settings.POSTGRES_COMMAND_TIMEOUT
    
    return kwargs
