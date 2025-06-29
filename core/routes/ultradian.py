from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import date, datetime

from core.extensions import db
from core.functions import generate_ultradian_cycles
from core.models import UserDailyRecord, UserCycleEvent

ultradian = Blueprint("ultradian", __name__, url_prefix="/api/ultradian")


@ultradian.route("/", methods=["GET"])
@login_required
def get_ultradian_cycles():
    """
    Gets ultradian cycle for either a date specified in the query parameters or today's date if none is provided.
    If no wake time is logged or no record exists for that date, returns 204 No Content.
    """
    try:
        # Parse date from query params
        month = int(request.args.get("m", date.today().month))
        year = int(request.args.get("y", date.today().year))
        day = int(request.args.get("d", date.today().day))
        ultradian_date = datetime(year, month, day).date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    user = current_user

    # Fetch daily record
    record = UserDailyRecord.query.filter_by(
        user_id=user.id, date=ultradian_date
    ).first()
    if not record or not record.wake_time:
        return jsonify({"message": "No ultradian data exists for this date"}), 204

    wake_time = record.wake_time.strftime("%H:%M:%S")

    # Use user defaults unless overridden
    peak = int(request.args.get("peak", user.peak_duration))
    trough = int(request.args.get("trough", user.trough_duration))
    count = int(request.args.get("cycles", user.cycles))
    grog = int(request.args.get("grog", user.morning_grog))

    try:
        cycles = generate_ultradian_cycles(wake_time, peak, trough, count, grog)
        return jsonify({"status": "success", "cycles": cycles}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@ultradian.route("/", methods=["POST", "OPTIONS"])
@login_required
def ultradian_cycles():
    today = request.json.get("date", date.today())
    if isinstance(today, str):
        today = datetime.strptime(today, "%Y-%m-%d").date()
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
                    end_time=datetime.strptime(cycle["peak_end"], "%H:%M:%S").time(),
                )
            )
            db.session.add(
                UserCycleEvent(
                    user_daily_record_id=record.id,
                    event_type="trough",
                    start_time=datetime.strptime(
                        cycle["trough_start"], "%H:%M:%S"
                    ).time(),
                    end_time=datetime.strptime(cycle["trough_end"], "%H:%M:%S").time(),
                )
            )

        db.session.commit()

        return jsonify({"status": "success", "cycles": cycles}), 200

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
