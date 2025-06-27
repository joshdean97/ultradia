from flask.cli import FlaskGroup
from core import create_app
from core.extensions import db

from config import DevelopmentConfig

# Only use development config if explicitly told to
import os

env_config = os.getenv("FLASK_ENV", "production")

if env_config == "development":
    from config import DevelopmentConfig as Config
else:
    from config import ProductionConfig as Config

app = create_app(config=Config)
