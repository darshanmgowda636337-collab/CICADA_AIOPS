import os
from pathlib import Path
from dotenv import load_dotenv

# ==========================================
# CICADA AIOPS - CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")


class Config:

    # Flask Configuration
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-to-a-secure-random-secret-key"
    )

    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # MySQL Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "cicada_aiops")

    # Database connection settings
    MYSQL_CHARSET = "utf8mb4"

    # Session Configuration
    SESSION_PERMANENT = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv(
        "SESSION_COOKIE_SECURE", "False"
    ).lower() == "true"

    # Application Configuration
    APP_NAME = "CICADA AIOps"
    APP_VERSION = "1.0.0"

    # API Configuration
    API_PREFIX = "/api"

    # Telemetry Configuration
    TELEMETRY_REFRESH_INTERVAL = 5000

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Configuration selector
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": Config
}