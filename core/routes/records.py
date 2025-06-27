from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from ..models import db, UserDailyRecord

records = Blueprint("records", __name__, url_prefix="/records")


@records.route("/", methods=["GET"], endpoint="get_today_record")
@login_required
def get_today_record():
    today = date.today()
    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    if record:
        return jsonify(record.as_dict()), 200
    return jsonify({"error": "No record found for today"}), 404


@records.route("/", methods=["POST", "OPTIONS"], endpoint="create_or_update_record")
@login_required
def create_or_update_record():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight"}), 200

    data = request.get_json()
    today = date.today()

    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    if not record:
        record = UserDailyRecord(user_id=current_user.id, date=today)

    # Parse and assign data
    wake_time_str = data.get("wake_time")
    if wake_time_str:
        try:
            record.wake_time = datetime.strptime(wake_time_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Invalid time format. Expected HH:MM"}), 400

    record.hrv = data.get("hrv")
    record.rhr = data.get("rhr")
    record.sleep_duration = data.get("sleep_duration")
    record.mood = data.get("mood")  # Can be emoji

    db.session.add(record)
    db.session.commit()

    return jsonify({"message": "Record saved"}), 200


@records.route("/today", methods=["GET"], endpoint="get_today_record_explicit")
@login_required
def get_today_record_explicit():
    today = date.today()
    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    if record:
        return jsonify(record.as_dict()), 200
    return jsonify({"error": "No record found for today"}), 404
