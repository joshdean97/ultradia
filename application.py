from core import create_app
from config import ProductionConfig

application = create_app(config=ProductionConfig)
