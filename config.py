import os


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RUNNING = "Config is running"
    FLASK_APP = "dev"
    FLASK_ENV = "development"
