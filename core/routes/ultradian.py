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

    Returns:
        Response: A JSON response containing the ultradian cycles for the current user.
        If no wake time is logged for today, returns an error message.
    """
    try:
        # get date and validate day, month, year inputs
        month = request.args.get("m")
        if month and not month.isdigit():
            return jsonify({"error": "Month must be an integer"}), 400
        if month and (int(month) < 1 or int(month) > 12):
            return jsonify({"error": "Month must be between 1 and 12"}), 400
        month = int(month or date.today().month)

        year = int(request.args.get("y", date.today().year))
        if year < 1900 or year > date.today().year:
            return (
                jsonify({"error": "Year must be between 1900 and the current year"}),
                400,
            )

        day = int(request.args.get("d", date.today().day))
        if day < 1 or day > 31:
            return jsonify({"error": "Day must be between 1 and 31"}), 400
        if month == 2 and day > 29:
            return jsonify({"error": "February cannot have more than 29 days"}), 400
        if month in [4, 6, 9, 11] and day > 30:
            return jsonify({"error": "This month cannot have more than 30 days"}), 400
        if (
            month == 2
            and day == 29
            and not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
        ):
            return jsonify({"error": "February 29 is only valid in leap years"}), 400
        day = int(day or date.today().day)

        # Create a date object for the ultradian cycle

        ultradian_date = datetime(year, month, day).date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    user = current_user

    # Fetch wake_time from today's record
    record = UserDailyRecord.query.filter_by(
        user_id=user.id, date=ultradian_date
    ).first()
    if not record:
        return jsonify({"error": f"No wake time logged for {ultradian_date}"}), 404

    wake_time = record.wake_time.strftime("%H:%M:%S")

    # Use user defaults unless override is passed
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
