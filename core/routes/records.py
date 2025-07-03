from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    current_user,
)
from datetime import datetime, date
from ..models import db, UserDailyRecord

records = Blueprint("records", __name__, url_prefix="/api/records")


@records.route("/", methods=["GET"], endpoint="get_today_record")
@jwt_required()
def get_today_record():
    today = date.today()
    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    if record:
        return jsonify(record.as_dict()), 200
    return jsonify({"error": "No record found for today"}), 404


@records.route("/all", methods=["GET"])
@jwt_required()
def get_all_records():
    user_id = current_user.id
    records = (
        UserDailyRecord.query.filter_by(user_id=user_id)
        .order_by(UserDailyRecord.date.desc())
        .all()
    )

    return jsonify([r.as_dict() for r in records]), 200


@records.route("/", methods=["POST", "OPTIONS"], endpoint="create_or_update_record")
@jwt_required()
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
@jwt_required()
def get_today_record_explicit():
    today = date.today()
    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    if record:
        return jsonify(record.as_dict()), 200
    return jsonify({"error": "No record found for today"}), 404


@records.route("/<int:record_id>/", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_record(record_id):
    if request.method == "OPTIONS":
        return "", 204  # Allow CORS preflight to pass

    record = UserDailyRecord.query.filter_by(
        id=record_id, user_id=current_user.id
    ).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404

    data = request.get_json()

    wake_time_str = data.get("wake_time")
    if wake_time_str:
        try:
            record.wake_time = datetime.strptime(wake_time_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Invalid time format. Expected HH:MM"}), 400

    # Allow updating these fields
    for field in ["hrv", "rhr", "sleep_duration", "mood", "session_ended_at"]:
        if field in data:
            setattr(record, field, data[field])

    db.session.commit()
    return jsonify({"message": "Record updated"}), 200
