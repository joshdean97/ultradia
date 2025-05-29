from waitress import serve
from core import create_app
from config import ProductionConfig

app = create_app(config=ProductionConfig)
if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
