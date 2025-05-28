class Config:
    """Base configuration class."""

    SECRET_KEY = "joe[dfj940[fj]]"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RUNNING = "Config is running"
