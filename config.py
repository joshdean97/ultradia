import os
from datetime import timedelta


class Config:
    """Base configuration class."""

    # Core Flask config
    FLASK_APP = "run.py"

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Debug flag
    RUNNING = "Base Config is running"

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "Shhhhdonttell")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)


class DevelopmentConfig(Config):
    """Development configuration class."""

    SECRET_KEY = os.getenv("SECRET_KEY", "jdifhidhf")

    DEBUG = True
    FLASK_ENV = "development"
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI", "sqlite:///dev_site.db")
    RUNNING = "Development Config is running"
    URL = os.environ.get("DEV_URL")

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


class ProductionConfig(Config):
    """Production configuration class."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    FLASK_APP = "application.py"
    FLASK_ENV = "development"

    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DB_URI")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("Missing PROD_DB_URI environment variable")

    DEBUG = False
    RUNNING = "Production Config is running"
