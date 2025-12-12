"""Configuración de la aplicación con validación para producción."""
import os
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Optional


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
        default_factory=lambda: ["*"] if os.getenv("ENVIRONMENT") != "production" else [],
        description="Orígenes permitidos para CORS"
    )
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Habilitar métricas")
    METRICS_PORT: int = Field(default=9090, ge=1, le=65535, description="Puerto para métricas")
    
    # Cache
    CACHE_ENABLED: bool = Field(default=True, description="Habilitar caché")
    CACHE_DEFAULT_TTL: int = Field(default=300, ge=1, description="TTL por defecto en segundos (5 minutos)")
    CACHE_STATS_ENABLED: bool = Field(default=True, description="Habilitar estadísticas de caché")

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Valida que el entorno sea válido."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT debe ser uno de: {', '.join(allowed)}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Valida que el nivel de log sea válido."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL debe ser uno de: {', '.join(allowed)}")
        return v.upper()
    
    @validator("POSTGRES_PASSWORD")
    def validate_password(cls, v, values):
        """Valida que la contraseña no sea la por defecto en producción."""
        if values.get("ENVIRONMENT") == "production" and v == "postgres":
            raise ValueError("No se puede usar la contraseña por defecto en producción")
        return v
    
    @property
    def is_production(self) -> bool:
        """Indica si estamos en producción."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Indica si estamos en desarrollo."""
        return self.ENVIRONMENT == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # En producción, no permitir valores por defecto inseguros
        validate_assignment = True


settings = Settings()
