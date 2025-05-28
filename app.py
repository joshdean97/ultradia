from core import create_app
from config import Config, DevelopmentConfig, ProductionConfig

if __name__ == "__main__":
    app = create_app(config=DevelopmentConfig)
    app.run(debug=True, host="127.0.0.1", port=5000)
# This script is used to run the Flask application in development mode.
