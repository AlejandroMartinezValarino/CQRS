"""Tests para el sistema de caché."""
import pytest
import time
from common.utils.cache import InMemoryCache, CacheEntry


@pytest.fixture
def cache():
    """Fixture para InMemoryCache."""
    return InMemoryCache(default_ttl=60)


def test_cache_set_get(cache):
    """Test que set() y get() funcionan correctamente."""
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"


def test_cache_miss(cache):
    """Test que get() retorna None para keys inexistentes."""
    assert cache.get("nonexistent") is None


def test_cache_expiration(cache):
    """Test que las entradas expiran correctamente."""
    cache.set("expired_key", "value", ttl=1)
    assert cache.get("expired_key") == "value"
    
    time.sleep(1.1)
    assert cache.get("expired_key") is None


def test_cache_delete(cache):
    """Test que delete() elimina entradas."""
    cache.set("delete_key", "value")
    cache.delete("delete_key")
    assert cache.get("delete_key") is None


def test_cache_clear(cache):
    """Test que clear() limpia todo el caché."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()
    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_cache_stats(cache):
    """Test que get_stats() retorna estadísticas correctas."""
    cache.set("key1", "value1")
    cache.get("key1")
    cache.get("nonexistent")
    
    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["total_requests"] == 2
    assert stats["hit_rate"] == 50.0
    assert stats["entries"] == 1


def test_cache_entry_expiration():
    """Test que CacheEntry.is_expired() funciona correctamente."""
    entry = CacheEntry("value", ttl=1)
    assert not entry.is_expired()
    
    time.sleep(1.1)
    assert entry.is_expired()