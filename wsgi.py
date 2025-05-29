from core import create_app
from config import Config, DevelopmentConfig, ProductionConfig

app = create_app(config=ProductionConfig)
