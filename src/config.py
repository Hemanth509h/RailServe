import os

class Config:
    """Application configuration class."""
    
    # Required environment variables - fail if not set
    SECRET_KEY = os.environ.get("SESSION_SECRET")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    # Optional environment variables with sensible defaults
    FLASK_ENV: str = os.environ.get("FLASK_ENV", "production")
    GUNICORN_WORKERS: int = int(os.environ.get("GUNICORN_WORKERS", "4"))
    
    # Security settings
    SESSION_COOKIE_SECURE: bool = FLASK_ENV == "production"
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    PERMANENT_SESSION_LIFETIME: int = 3600  # 1 hour
    
    # Database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # CSRF Protection removed as requested
    
    @classmethod
    def validate_config(cls) -> None:
        """Validate that all required configuration is present."""
        missing_vars = []
        
        if not cls.SECRET_KEY:
            missing_vars.append("SESSION_SECRET")
        
        if not cls.DATABASE_URL:
            missing_vars.append("DATABASE_URL")
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                f"Please check your .env file or environment configuration."
            )