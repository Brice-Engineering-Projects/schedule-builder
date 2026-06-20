"""Application settings and configuration management.

Settings are loaded from environment variables, with sensible defaults
for development. Use environment-specific .env files to override defaults.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ############################################################################
    # ENVIRONMENT
    ############################################################################

    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode (should be False in production)",
    )

    ############################################################################
    # API CONFIGURATION
    ############################################################################

    api_title: str = Field(
        default="Schedule Builder API",
        description="API title for documentation",
    )
    api_version: str = Field(
        default="0.1.0",
        description="API version",
    )
    api_description: str = Field(
        default="Project planning and proposal support platform for engineering consultants",
        description="API description for documentation",
    )

    api_docs_url: str = Field(
        default="/docs",
        description="URL for Swagger UI documentation",
    )
    api_redoc_url: str = Field(
        default="/redoc",
        description="URL for ReDoc documentation",
    )
    api_openapi_url: str = Field(
        default="/openapi.json",
        description="URL for OpenAPI schema",
    )

    ############################################################################
    # SERVER CONFIGURATION
    ############################################################################

    server_host: str = Field(
        default="0.0.0.0",
        description="Server host address",
    )
    server_port: int = Field(
        default=8000,
        description="Server port",
    )
    server_reload: bool = Field(
        default=True,
        description="Auto-reload on file changes (dev only)",
    )

    ############################################################################
    # CORS CONFIGURATION
    ############################################################################

    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )
    cors_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests",
    )
    cors_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        description="Allowed HTTP methods",
    )
    cors_headers: list[str] = Field(
        default=["*"],
        description="Allowed headers",
    )

    ############################################################################
    # DATABASE CONFIGURATION
    ############################################################################

    database_url: str = Field(
        default="sqlite:///./test.db",
        description="Database connection URL",
    )
    database_echo: bool = Field(
        default=False,
        description="Log all SQL statements",
    )
    database_pool_size: int = Field(
        default=5,
        description="Connection pool size",
    )
    database_pool_recycle: int = Field(
        default=3600,
        description="Recycle connections after N seconds",
    )

    ############################################################################
    # AUTHENTICATION & SECURITY
    ############################################################################

    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT signing",
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="JWT access token expiration in minutes",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="JWT refresh token expiration in days",
    )

    ############################################################################
    # THIRD-PARTY INTEGRATIONS
    ############################################################################

    # Anthropic (Claude)
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key for Claude",
    )
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Anthropic model ID",
    )

    # OpenAI
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key",
    )
    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model ID",
    )

    # SendGrid (Email)
    sendgrid_api_key: str = Field(
        default="",
        description="SendGrid API key for email notifications",
    )
    sendgrid_from_email: str = Field(
        default="noreply@schedulebuilder.com",
        description="Default sender email address",
    )

    # Stripe (Payments)
    stripe_api_key: str = Field(
        default="",
        description="Stripe API key for payments",
    )
    stripe_webhook_secret: str = Field(
        default="",
        description="Stripe webhook signing secret",
    )

    ############################################################################
    # LOGGING CONFIGURATION
    ############################################################################

    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )

    ############################################################################
    # FILE UPLOAD CONFIGURATION
    ############################################################################

    max_upload_size_mb: int = Field(
        default=50,
        description="Maximum file upload size in MB",
    )
    allowed_file_extensions: list[str] = Field(
        default=["pdf", "docx", "xlsx", "csv"],
        description="Allowed file extensions for uploads",
    )
    upload_directory: str = Field(
        default="uploads",
        description="Directory for file uploads",
    )

    ############################################################################
    # FEATURE FLAGS
    ############################################################################

    enable_email_notifications: bool = Field(
        default=True,
        description="Enable email notifications",
    )
    enable_ai_features: bool = Field(
        default=True,
        description="Enable AI-powered features",
    )
    enable_stripe_payments: bool = Field(
        default=False,
        description="Enable Stripe payment processing",
    )

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
