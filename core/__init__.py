from flask import Flask, request, jsonify

from .extensions import db, migrate, cors
from .functions import generate_ultradian_cycles


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object("config.Config")
    print(app.config["RUNNING"])  # Print the running message from Config
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    @app.route("/api/ultradian", methods=["POST"])
    def ultradian_cycles():
        wake_time = request.json.get("wake_time", "06:00:00")
        peak = int(request.json.get("peak", 90))
        trough = int(request.json.get("trough", 20))
        count = int(request.json.get("cycles", 5))
        grog = int(request.json.get("grog", 20))

        try:
            cycles = generate_ultradian_cycles(wake_time, peak, trough, count, grog)
            return jsonify({"status": "success", "cycles": cycles}), 200
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    return app
