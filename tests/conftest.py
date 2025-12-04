"""Configuración de pytest para tests."""
import pytest
import asyncio
from typing import AsyncGenerator
from config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Crea un event loop para tests asíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Configuración de prueba."""
    return settings

