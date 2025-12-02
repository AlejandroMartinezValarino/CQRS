"""Utilidades para retry con exponential backoff."""
import asyncio
import functools
from typing import Callable, TypeVar, Any
from common.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def retry_async(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para retry asíncrono con exponential backoff.
    
    Args:
        max_attempts: Número máximo de intentos
        initial_delay: Delay inicial en segundos
        max_delay: Delay máximo en segundos
        exponential_base: Base para el exponential backoff
        exceptions: Tupla de excepciones que deben activar el retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"Falló después de {max_attempts} intentos: {func.__name__}",
                            exc_info=True
                        )
                        raise
                    
                    logger.warning(
                        f"Intento {attempt}/{max_attempts} falló para {func.__name__}: {e}. "
                        f"Reintentando en {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)
            
            # No debería llegar aquí, pero por si acaso
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


def retry_sync(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para retry síncrono con exponential backoff.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"Falló después de {max_attempts} intentos: {func.__name__}",
                            exc_info=True
                        )
                        raise
                    
                    logger.warning(
                        f"Intento {attempt}/{max_attempts} falló para {func.__name__}: {e}. "
                        f"Reintentando en {delay:.2f}s..."
                    )
                    import time
                    time.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)
            
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator

