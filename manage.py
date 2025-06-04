from flask.cli import FlaskGroup
from core import create_app
from core.extensions import db

from config import DevelopmentConfig

app = create_app(config=DevelopmentConfig)
cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()
