"""Evento base del dominio."""
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field
import uuid


class BaseEvent(BaseModel):
    """Clase base para todos los eventos."""
    
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    aggregate_id: str
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

