"""Servicio de caché in-memory con TTL."""
import time
from typing import Optional, Dict, Any
from threading import Lock
from common.utils.logger import get_logger

logger = get_logger(__name__)


class CacheEntry:
    """Entrada del caché con timestamp de expiración."""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        return time.time() > self.expires_at


class InMemoryCache:
    """Caché in-memory con TTL y métricas."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                logger.debug(f"Cache MISS para key: {key}")
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache MISS (expired) para key: {key}")
                return None
            
            self._hits += 1
            logger.debug(f"Cache HIT para key: {key}")
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Guarda un valor en el caché."""
        with self._lock:
            ttl = ttl or self.default_ttl
            self._cache[key] = CacheEntry(value, ttl)
            logger.debug(f"Cache SET para key: {key} con TTL: {ttl}s")
    
    def delete(self, key: str) -> None:
        """Elimina una entrada del caché."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache DELETE para key: {key}")
    
    def clear(self) -> None:
        """Limpia todo el caché."""
        with self._lock:
            self._cache.clear()
            logger.info("Cache CLEAR ejecutado")
    
    def _cleanup_expired(self) -> None:
        """Limpia entradas expiradas."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cache cleanup: {len(expired_keys)} entradas expiradas eliminadas")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché."""
        self._cleanup_expired()
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        with self._lock:
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total_requests,
                "hit_rate": round(hit_rate, 2),
                "entries": len(self._cache),
                "default_ttl": self.default_ttl,
            }
    
    def reset_stats(self) -> None:
        """Resetea las estadísticas."""
        with self._lock:
            self._hits = 0
            self._misses = 0
            logger.debug("Cache stats reseteadas")