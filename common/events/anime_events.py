"""Eventos relacionados con animes."""
from datetime import datetime
from .base_event import BaseEvent
from pydantic import Field


class ClickRegistered(BaseEvent):
    """Evento cuando un usuario hace click en un anime."""
    
    event_type: str = "ClickRegistered"
    anime_id: int
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ViewRegistered(BaseEvent):
    """Evento cuando un usuario visualiza un anime."""
    
    event_type: str = "ViewRegistered"
    anime_id: int
    user_id: str
    duration_seconds: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RatingGiven(BaseEvent):
    """Evento cuando un usuario califica un anime."""
    
    event_type: str = "RatingGiven"
    anime_id: int
    user_id: str
    rating: float = Field(ge=0.0, le=10.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

