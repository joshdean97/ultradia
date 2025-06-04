from flask import Flask, request, jsonify
from flask_login import LoginManager, current_user, login_required
from dotenv import load_dotenv


from .extensions import db, migrate, cors
from .functions import generate_ultradian_cycles
from .models import User, UserDailyRecord, UserCycleEvent
from .routes import auth, records, cycles, users as user_bp

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
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # initialize blueprints
    app.register_blueprint(auth)
    app.register_blueprint(records)
    app.register_blueprint(cycles)
    app.register_blueprint(user_bp)

    @app.route("/api/health", methods=["GET"])
    def status():
        return jsonify({"status": "running"}), 200

    @app.route("/api/ultradian", methods=["POST"])
    @login_required
    def ultradian_cycles():
        today = date.today()
        user = current_user

        # Fetch wake_time from today's record
        record = UserDailyRecord.query.filter_by(user_id=user.id, date=today).first()
        if not record:
            return jsonify({"error": "No wake time logged for today"}), 404

        wake_time = record.wake_time.strftime("%H:%M:%S")

        # Use user defaults unless override is passed
        peak = int(request.json.get("peak", user.peak_duration))
        trough = int(request.json.get("trough", user.trough_duration))
        count = int(request.json.get("cycles", user.cycles))
        grog = int(request.json.get("grog", user.morning_grog))

        try:
            cycles = generate_ultradian_cycles(wake_time, peak, trough, count, grog)

            # Clear existing events for today (optional safety step)
            UserCycleEvent.query.filter_by(user_daily_record_id=record.id).delete()

            for cycle in cycles:
                db.session.add(
                    UserCycleEvent(
                        user_daily_record_id=record.id,
                        event_type="peak",
                        start_time=datetime.strptime(
                            cycle["peak_start"], "%H:%M:%S"
                        ).time(),
                        end_time=datetime.strptime(
                            cycle["peak_end"], "%H:%M:%S"
                        ).time(),
                    )
                )
                db.session.add(
                    UserCycleEvent(
                        user_daily_record_id=record.id,
                        event_type="trough",
                        start_time=datetime.strptime(
                            cycle["trough_start"], "%H:%M:%S"
                        ).time(),
                        end_time=datetime.strptime(
                            cycle["trough_end"], "%H:%M:%S"
                        ).time(),
                    )
                )

            db.session.commit()

            return jsonify({"status": "success", "cycles": cycles}), 200

        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    return app
