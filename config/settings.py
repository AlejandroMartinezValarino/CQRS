"""Configuración de la aplicación con validación para producción."""
import os
import json
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from typing import Optional, Union


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Entorno: development, staging, production")
    DEBUG: bool = Field(default=False, description="Modo debug")
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging: DEBUG, INFO, WARNING, ERROR")
    
    # Database - Read Model
    POSTGRES_HOST: str = Field(default="localhost", description="Host de PostgreSQL")
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535, description="Puerto de PostgreSQL")
    POSTGRES_USER: str = Field(default="Molkiu", description="Usuario de PostgreSQL")
    POSTGRES_PASSWORD: str = Field(default="postgres", description="Contraseña de PostgreSQL")
    POSTGRES_DB: str = Field(default="cqrs_db", description="Base de datos principal")
    POSTGRES_MAX_CONNECTIONS: int = Field(default=20, ge=1, le=100, description="Máximo de conexiones en el pool")
    POSTGRES_MIN_CONNECTIONS: int = Field(default=5, ge=1, description="Mínimo de conexiones en el pool")
    POSTGRES_COMMAND_TIMEOUT: int = Field(default=30, ge=1, description="Timeout de comandos en segundos")
    
    # Database - Event Store
    POSTGRES_EVENT_STORE_DB: str = Field(default="cqrs_event_store", description="Base de datos del Event Store")
    POSTGRES_EVENT_STORE_MAX_CONNECTIONS: int = Field(default=10, ge=1, le=100)
    POSTGRES_EVENT_STORE_MIN_CONNECTIONS: int = Field(default=2, ge=1)
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092", description="Servidores de Kafka")
    KAFKA_TOPIC_EVENTS: str = Field(default="anime-events", description="Topic para eventos")
    KAFKA_PRODUCER_RETRIES: int = Field(default=3, ge=0, description="Intentos de retry para producer")
    KAFKA_CONSUMER_GROUP_ID: str = Field(default="read-side-consumer-group", description="Group ID del consumer")
    KAFKA_CONSUMER_AUTO_OFFSET_RESET: str = Field(default="earliest", description="Auto offset reset")
    KAFKA_CONSUMER_ENABLE_AUTO_COMMIT: bool = Field(default=False, description="Auto commit de offsets")
    
    # API - Command Side
    API_HOST: str = Field(default="0.0.0.0", description="Host del API")
    API_PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")), ge=1, le=65535, description="Puerto del API")
    API_WORKERS: int = Field(default=4, ge=1, le=32, description="Número de workers")
    API_RELOAD: bool = Field(default=False, description="Auto-reload (solo desarrollo)")
    
    # GraphQL - Read Side
    GRAPHQL_HOST: str = Field(default="0.0.0.0", description="Host de GraphQL")
    GRAPHQL_PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", "8001")), ge=1, le=65535, description="Puerto de GraphQL")
    GRAPHQL_WORKERS: int = Field(default=4, ge=1, le=32, description="Número de workers")
    
    # Security
    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: (
            ["*"] if os.getenv("ENVIRONMENT") != "production" 
            else ["https://cqrs.alejandrotech.eu", "https://www.cqrs.alejandrotech.eu"]
        ),
        description="Orígenes permitidos para CORS"
    )
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, list, None]) -> Union[list, None]:
        """Parsea ALLOWED_ORIGINS desde JSON o string separado por comas."""
        # Si no hay valor, retornar None para usar default_factory
        if v is None:
            return None
        
        # Si ya es una lista, retornarla directamente
        if isinstance(v, list):
            return v
        
        # Si es un string
        if isinstance(v, str):
            # Si está vacío, retornar None para usar default_factory
            v_stripped = v.strip()
            if not v_stripped:
                return None
            
            # Intentar parsear como JSON primero
            try:
                parsed = json.loads(v_stripped)
                if isinstance(parsed, list):
                    return parsed
                # Si es JSON pero no una lista, retornar None
                return None
            except (json.JSONDecodeError, ValueError):
                # Si no es JSON válido, tratar como string separado por comas
                origins = [origin.strip() for origin in v_stripped.split(",") if origin.strip()]
                return origins if origins else None
        
        # Para cualquier otro tipo, retornar None para usar default_factory
        return None
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Habilitar métricas")
    METRICS_PORT: int = Field(default=9090, ge=1, le=65535, description="Puerto para métricas")
    
    # Cache
    CACHE_ENABLED: bool = Field(default=True, description="Habilitar caché")
    CACHE_DEFAULT_TTL: int = Field(default=300, ge=1, description="TTL por defecto en segundos (5 minutos)")
    CACHE_STATS_ENABLED: bool = Field(default=True, description="Habilitar estadísticas de caché")

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Valida que el entorno sea válido."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT debe ser uno de: {', '.join(allowed)}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida que el nivel de log sea válido."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL debe ser uno de: {', '.join(allowed)}")
        return v.upper()
    
    @model_validator(mode='after')
    def validate_password(self):
        """Valida que la contraseña no sea la por defecto en producción."""
        if self.ENVIRONMENT == "production" and self.POSTGRES_PASSWORD == "postgres":
            raise ValueError("No se puede usar la contraseña por defecto en producción")
        return self
    
    @property
    def is_production(self) -> bool:
        """Indica si estamos en producción."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Indica si estamos en desarrollo."""
        return self.ENVIRONMENT == "development"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "validate_assignment": True,
    }


settings = Settings()
