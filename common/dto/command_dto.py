"""DTOs para comandos."""
from pydantic import BaseModel, Field
from datetime import datetime


class ClickCommand(BaseModel):
    """Comando para registrar un click."""
    
    anime_id: int
    user_id: str


class ViewCommand(BaseModel):
    """Comando para registrar una visualización."""
    
    anime_id: int
    user_id: str
    duration_seconds: int = Field(ge=0)


class RatingCommand(BaseModel):
    """Comando para registrar una calificación."""
    
    anime_id: int
    user_id: str
    rating: float = Field(ge=0.0, le=10.0)

