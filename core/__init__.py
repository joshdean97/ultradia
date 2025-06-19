from flask import Flask, request, jsonify
from flask_login import LoginManager, current_user, login_required
from dotenv import load_dotenv
import csv, pathlib
import os


from .extensions import db, migrate, cors
from .functions import generate_ultradian_cycles
from .models import User, UserDailyRecord, UserCycleEvent, Leads
from .routes import (
    auth as auth_bp,
    records as records_bp,
    cycles as cycles_bp,
    users as user_bp,
    ultradian as ultradian_bp,
    vital as vital_bp,
)

from datetime import date, datetime, timedelta
import requests
import time

# if os.getenv("FLASK_ENV") == "development":
load_dotenv()

def create_app(config=None):
    app = Flask(__name__)
    
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)


    # Load configuration
    if config is None:
        from config import DevelopmentConfig

        config = DevelopmentConfig

    app.config.from_object(config)
    
    print(app.config["RUNNING"])  # Print the running message from Config
    # Initialize extensions
    print("Using DB:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, supports_credentials=True, resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "https://ultradia.app"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })    
    app.url_map.strict_slashes = False

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
    app.register_blueprint(vital_bp)

    @app.route("/health", methods=["GET"])
    def status():
        return jsonify({"status": "running"}), 200

    CSV_PATH = pathlib.Path("leads.csv")

    @app.route("/leads", methods=["POST"])
    def get_leads():
        email = request.json.get("email", "").strip().lower()
        name = request.json.get("name", "").strip().title()
        ts = datetime.now().isoformat()

        new_lead = Leads(
            email = email,
            name = name
        )
        
        db.session.add(new_lead)
        db.session.commit()
        
        return jsonify(
            {
                "message": "Successfully added",
                "name": name,
                "email": email
            }
        ), 200

    return app
