import os


class Config:
    """Base configuration class."""

    # Core Flask config
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    DEBUG = False
    FLASK_APP = "run.py"
    FLASK_ENV = "production"

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI", "sqlite:///default.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Debug flag
    RUNNING = "Base Config is running"


class DevelopmentConfig(Config):
    """Development configuration class."""

    DEBUG = True
    FLASK_ENV = "development"
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DB_URI", "sqlite:///dev_site.db")
    RUNNING = "Development Config is running"


class ProductionConfig(Config):
    """Production configuration class."""

    DEBUG = False
    FLASK_ENV = "production"
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DB_URI", "sqlite:///prod_site.db")
    RUNNING = "Production Config is running"
