from flask import Flask, request, jsonify
from flask_login import LoginManager, current_user, login_required
from dotenv import load_dotenv


from .extensions import db, migrate, cors
from .functions import generate_ultradian_cycles
from .models import User, UserDailyRecord, UserCycleEvent
from .routes import (
    auth as auth_bp,
    records as records_bp,
    cycles as cycles_bp,
    users as user_bp,
    ultradian as ultradian_bp,
)

from datetime import date, datetime

load_dotenv()  # Load environment variables from .env file


def create_app(config=None):
    app = Flask(__name__)

    # Load configuration
    if config is None:
        from config import DevelopmentConfig

        config = DevelopmentConfig

    app.config.from_object(config)

    print(app.config["RUNNING"])  # Print the running message from Config
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": "http://localhost:3000"}},
        supports_credentials=True,
    )
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Unauthorized"}), 401

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # initialize blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(cycles_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(ultradian_bp)

    @app.route("/api/health", methods=["GET"])
    def status():
        return jsonify({"status": "running"}), 200

    return app
