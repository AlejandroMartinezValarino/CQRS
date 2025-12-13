"""Utilidades para conexiones a base de datos."""
from typing import Dict, Any, Optional
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import os
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
    
    Prioridad:
    1. Variables de entorno PGHOST, PGPORT, etc. (Railway las proporciona)
    2. DATABASE_URL (si está disponible)
    3. Variables individuales de configuración (settings)
    
    Args:
        database: Nombre de la base de datos (opcional, sobrescribe la del DATABASE_URL)
        min_size: Tamaño mínimo del pool (opcional)
        max_size: Tamaño máximo del pool (opcional)
        command_timeout: Timeout de comandos (opcional)
    
    Returns:
        Diccionario con los parámetros para asyncpg.create_pool
    """
    kwargs: Dict[str, Any] = {}
    
    # Prioridad 1: Variables de entorno de Railway (PGHOST, PGPORT, etc.)
    # Railway proporciona estas variables cuando conectas un servicio PostgreSQL
    pghost = os.getenv('PGHOST')
    pgport = os.getenv('PGPORT')
    pguser = os.getenv('PGUSER')
    pgpassword = os.getenv('PGPASSWORD')
    
    if pghost:
        kwargs['host'] = pghost
        kwargs['port'] = int(pgport) if pgport else settings.POSTGRES_PORT
        kwargs['user'] = pguser or settings.POSTGRES_USER
        kwargs['password'] = pgpassword or settings.POSTGRES_PASSWORD
        kwargs['database'] = database or settings.POSTGRES_DB
    
    # Prioridad 2: DATABASE_URL (si no se usaron variables PGHOST)
    if 'host' not in kwargs:
        database_url = getattr(settings, 'DATABASE_URL', None)
        if database_url and not database_url.startswith("${{"):
            try:
                # Parsear la URL (puede ser postgresql:// o postgres://)
                parsed = urlparse(database_url)
                
                # Extraer componentes de la URL y usar parámetros individuales
                # Esto evita que asyncpg parse la DSN y extraiga parámetros inválidos de la query string
                kwargs['host'] = parsed.hostname or settings.POSTGRES_HOST
                kwargs['port'] = parsed.port or settings.POSTGRES_PORT
                kwargs['user'] = parsed.username or settings.POSTGRES_USER
                kwargs['password'] = parsed.password or settings.POSTGRES_PASSWORD
                
                # Determinar la base de datos
                db_name = database or (parsed.path.lstrip('/') if parsed.path else settings.POSTGRES_DB)
                kwargs['database'] = db_name
                
            except Exception:
                # Si hay error parseando DATABASE_URL, usar variables individuales
                pass
    
    # Prioridad 3: Variables individuales de configuración (fallback)
    if 'host' not in kwargs:
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
    
    # Asegurarse de que no se pasen parámetros inválidos a asyncpg
    # Estos parámetros no son soportados por asyncpg.create_pool
    invalid_kwargs = {'connect_timeout', 'max_queries', 'max_inactive_connection_lifetime', 'server_settings'}
    for invalid_key in invalid_kwargs:
        kwargs.pop(invalid_key, None)
    
    return kwargs
