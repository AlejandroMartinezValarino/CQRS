"""Eventos del dominio."""
from .base_event import BaseEvent
from .anime_events import (
    ClickRegistered,
    ViewRegistered,
    RatingGiven,
)

__all__ = [
    "BaseEvent",
    "ClickRegistered",
    "ViewRegistered",
    "RatingGiven",
]

