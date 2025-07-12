from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    current_user,
)
from datetime import date, datetime

from core.extensions import db
from core.models import UserDailyRecord, UserCycleEvent

cycles = Blueprint("cycles", __name__, url_prefix="/api/cycles")


@cycles.route("/", methods=["GET"])
@jwt_required()
def get_all_cycles():
    """Get all cycle events for the current user."""
    records = UserDailyRecord.query.filter_by(user_id=current_user.id).all()
    events = []

    for record in records:
        for event in record.cycle_events:
            events.append(
                {
                    "date": record.date.isoformat(),
                    "event_type": event.event_type,
                    "start_time": event.start_time.strftime("%H:%M:%S"),
                    "end_time": event.end_time.strftime("%H:%M:%S"),
                }
            )

    return jsonify(events), 200


@cycles.route("/today", methods=["GET"])
@jwt_required()
def get_todays_cycles():
    """Get today's cycle events for the current user."""
    today = date.today()
    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    if not record:
        return jsonify({"message": "No record for today"}), 404

    events = [
        {
            "event_type": event.event_type,
            "start_time": event.start_time.strftime("%H:%M:%S"),
            "end_time": event.end_time.strftime("%H:%M:%S"),
        }
        for event in record.cycle_events
    ]
    wake_time = record.wake_time.strftime("%H:%M:%S") if record.wake_time else None

    return (
        jsonify({"date": today.isoformat(), "wake time": wake_time, "events": events}),
        200,
    )


@cycles.route("/", methods=["POST"])
@jwt_required()
def add_cycle_event():
    """Add a new cycle event to today’s record."""
    data = request.get_json()
    from datetime import datetime

    start_time = datetime.strptime(data.get("start_time"), "%H:%M:%S").time()
    try:
        start_time = datetime.strptime(data.get("start_time"), "%H:%M:%S").time()
        end_time = datetime.strptime(data.get("end_time"), "%H:%M:%S").time()
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing time format. Use HH:MM:SS"}), 400

    event_type = data.get("event_type")
    if event_type not in ["peak", "trough"]:
        return jsonify({"error": "Invalid event type"}), 400

    today = date.today()
    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, date=today
    ).first()
    if not record:
        return jsonify({"error": "No daily record found for today"}), 404

    new_event = UserCycleEvent(
        user_daily_record_id=record.id,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
    )
    db.session.add(new_event)
    db.session.commit()

    return jsonify({"message": "Cycle event added successfully"}), 201


@cycles.route("/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_cycle_event(event_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    event = UserCycleEvent.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    # Manual auth check since no direct record relationship
    record = UserDailyRecord.query.get(event.user_daily_record_id)
    if not record or record.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        if "start_time" in data:
            event.start_time = datetime.strptime(data["start_time"], "%H:%M:%S").time()
        if "end_time" in data:
            event.end_time = datetime.strptime(data["end_time"], "%H:%M:%S").time()
        if "event_type" in data:
            event.event_type = data["event_type"]

        db.session.commit()
        return jsonify({"message": "Cycle event updated"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
