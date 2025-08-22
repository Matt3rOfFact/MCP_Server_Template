"""Configuration management for MCP Server."""

from typing import Any, Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class Environment(str, Enum):
    """Application environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuthConfig(BaseModel):
    """Authentication configuration."""
    enabled: bool = False
    type: str = "bearer"
    token: Optional[str] = None
    oauth_providers: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    debug: bool = False


class MiddlewareConfig(BaseModel):
    """Middleware configuration."""
    logging_enabled: bool = True
    logging_level: LogLevel = LogLevel.INFO
    rate_limiting_enabled: bool = False
    requests_per_minute: int = 60
    cors_enabled: bool = True
    cors_origins: List[str] = ["*"]


class ResourceConfig(BaseModel):
    """Resource configuration."""
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    max_file_size_mb: int = 10
    allowed_file_extensions: List[str] = [".txt", ".json", ".md", ".py"]


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "MCP Server Template"
    app_version: str = "0.1.0"
    environment: Environment = Environment.DEVELOPMENT
    
    # Server
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    # Authentication
    auth: AuthConfig = Field(default_factory=AuthConfig)
    auth_token: Optional[str] = Field(None, env="MCP_AUTH_TOKEN")
    
    # OAuth
    github_client_id: Optional[str] = Field(None, env="GITHUB_CLIENT_ID")
    github_client_secret: Optional[str] = Field(None, env="GITHUB_CLIENT_SECRET")
    google_client_id: Optional[str] = Field(None, env="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(None, env="GOOGLE_CLIENT_SECRET")
    
    # Middleware
    middleware: MiddlewareConfig = Field(default_factory=MiddlewareConfig)
    
    # Resources
    resources: ResourceConfig = Field(default_factory=ResourceConfig)
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".mcp_server_template")
    log_dir: Path = Field(default_factory=lambda: Path.home() / ".mcp_server_template" / "logs")
    
    # Database (optional)
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    
    # External APIs (optional)
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    @validator("data_dir", "log_dir", pre=False, always=True)
    def create_directories(cls, v: Path) -> Path:
        """Create directories if they don't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator("server", pre=True)
    def configure_server_by_environment(cls, v: Dict[str, Any], values: Dict[str, Any]) -> ServerConfig:
        """Configure server based on environment."""
        if isinstance(v, ServerConfig):
            return v
            
        env = values.get("environment", Environment.DEVELOPMENT)
        
        if env == Environment.PRODUCTION:
            return ServerConfig(
                host="0.0.0.0",
                port=8000,
                workers=4,
                reload=False,
                debug=False
            )
        elif env == Environment.STAGING:
            return ServerConfig(
                host="0.0.0.0",
                port=8000,
                workers=2,
                reload=False,
                debug=False
            )
        else:  # Development
            return ServerConfig(
                host="localhost",
                port=8000,
                workers=1,
                reload=True,
                debug=True
            )
    
    def get_oauth_config(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get OAuth configuration for a specific provider."""
        configs = {
            "github": {
                "client_id": self.github_client_id,
                "client_secret": self.github_client_secret,
                "scopes": ["user:email", "read:user"]
            },
            "google": {
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "scopes": ["openid", "email", "profile"]
            }
        }
        
        config = configs.get(provider)
        if config and config["client_id"] and config["client_secret"]:
            return config
        return None


# Global settings instance
settings = Settings()