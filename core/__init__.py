from flask import Flask, request, jsonify
from flask_login import LoginManager, current_user, login_required
from dotenv import load_dotenv


from .extensions import db, migrate, cors
from .functions import generate_ultradian_cycles
from .models import User, UserDailyRecord, UserCycleEvent
from .routes import auth, records, rhythms, users as user_bp

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
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # initialize blueprints
    app.register_blueprint(auth)
    app.register_blueprint(records)
    app.register_blueprint(rhythms)
    app.register_blueprint(user_bp)

    @app.route("/api/health", methods=["GET"])
    def status():
        return jsonify({"status": "running"}), 200

    @app.route("/api/<user_id>/ultradian", methods=["POST"])
    def ultradian_cycles(user_id):
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get latest record
        latest_record = (
            UserDailyRecord.query.filter_by(user_id=user.id)
            .order_by(UserDailyRecord.date.desc())
            .first()
        )
        if not latest_record or not latest_record.wake_time:
            return jsonify({"error": "Wake time not found"}), 400

        wake_time = latest_record.wake_time.strftime("%H:%M:%S")
        peak = user.peak_duration
        trough = user.trough_duration
        count = user.cycles
        grog = user.morning_grog

        try:
            cycles = generate_ultradian_cycles(wake_time, peak, trough, count, grog)
            return jsonify({"status": "success", "cycles": cycles}), 200
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    return app
