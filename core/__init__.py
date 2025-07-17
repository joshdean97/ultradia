from flask import Flask, request, jsonify, abort, render_template

from werkzeug.security import check_password_hash

from dotenv import load_dotenv
import csv, pathlib
import os

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from .extensions import db, migrate, cors, jwt
from .functions import generate_ultradian_cycles
from .models import User, UserDailyRecord, UserCycleEvent, Leads
from .routes import (
    auth as auth_bp,
    records as records_bp,
    cycles as cycles_bp,
    users as user_bp,
    ultradian as ultradian_bp,
    vital as vital_bp,
    vibe_bp,
    analytics_bp,
    admin_bp,
)
from core.routes.auth import oauth

from datetime import date, datetime, timedelta
import requests
import time

# if os.getenv("FLASK_ENV") == "development":
load_dotenv()


def create_app(config=None):
    app = Flask(__name__)

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
    cors.init_app(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "https://ultradia.app",
                    "http://localhost:5000",
                    "https://api.ultradia.app",
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )
    jwt.init_app(app)
    oauth.init_app(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    app.url_map.strict_slashes = False

    API_SECRET = os.getenv("API_SHARED_SECRET")
    print("Google Client ID:", os.getenv("GOOGLE_CLIENT_ID"))

    @app.before_request
    def verify_origin():
        if request.method == "OPTIONS":
            return
        if request.path.startswith(
            ("/admin", "/static", "/health", "/temp", "api/auth/login/google")
        ):
            return

        user_agent = request.headers.get("User-Agent", "").lower()
        honeypot_agents = ["zgrab", "sqlmap", "nmap", "curl", "python-requests"]

        if any(bot in user_agent for bot in honeypot_agents):
            app.logger.warning(
                f"🕵️ Honeypot tripped by: {user_agent} from {request.remote_addr}"
            )
            time.sleep(3)
            return "404 Not Found: Nope. Try again, bot 🤖", 404

        IS_DEV = os.getenv("FLASK_ENV") == "development"
        referer = request.headers.get("Referer", "")
        header_token = request.headers.get("X-Ultra-Secret", "")

        allowed_referers = [
            "https://ultradia.app",
            "https://www.ultradia.app",
            "https://api.ultradia.app",
        ]

        if IS_DEV:
            allowed_referers += [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5000",
                "http://127.0.0.1:5000",
            ]
        else:
            if not isinstance(referer, str) or not any(
                referer.startswith(origin) for origin in allowed_referers
            ):
                app.logger.warning(
                    f"❌ Blocked by referer: {referer} from {request.remote_addr}"
                )
                abort(403)

        # ✅ Skip this block for Flask Admin
        if not IS_DEV:
            if request.path.startswith("/temp-login"):
                # allow open access to /temp-login in prod
                return

            if (
                not request.path.startswith("/admin")
                and not referer.startswith("https://ultradia.app")
                and header_token != os.getenv("API_SHARED_SECRET")
            ):
                abort(403)

    @app.after_request
    def apply_cors(response):
        origin = request.headers.get("Origin")
        allowed = [
            "https://ultradia.app",
            "https://www.ultradia.app",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

        if origin in allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"

        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )

        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Ultra-Secret"
        )

        return response

    # initialize blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(cycles_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(ultradian_bp)
    app.register_blueprint(vital_bp)
    app.register_blueprint(vibe_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)

    @app.route("/health", methods=["GET"])
    def status():
        return jsonify({"status": "running"}), 200

    CSV_PATH = pathlib.Path("leads.csv")

    @app.route("/leads", methods=["POST"])
    def get_leads():
        email = request.json.get("email", "").strip().lower()
        name = request.json.get("name", "").strip().title()
        ts = datetime.now().isoformat()

        new_lead = Leads(email=email, name=name)

        db.session.add(new_lead)
        db.session.commit()

        return (
            jsonify({"message": "Successfully added", "name": name, "email": email}),
            200,
        )

    @app.route("/temp-login", methods=["GET", "POST"])
    def temp_login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            user = User.query.filter_by(email=email).first()
            if not user:
                return "no user found", 401

            if check_password_hash(user.password_hash, password):
                access_token = access_token = create_access_token(identity=str(user.id))
                return jsonify({"access_token": access_token, "user_id": user.id})
            else:
                return "Incorrect Password", 401

        return render_template("temp-login.html")

    return app
