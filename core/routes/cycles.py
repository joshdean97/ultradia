from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import date

from core.extensions import db
from core.models import UserDailyRecord, UserCycleEvent

cycles = Blueprint("cycles", __name__, url_prefix="/api/cycles")


@cycles.route("/", methods=["GET"])
@login_required
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
@login_required
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


@cycles.route("/add", methods=["POST"])
@login_required
def add_cycle_event():
    """Add a new cycle event to today’s record."""
    data = request.get_json()
    event_type = data.get("event_type")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

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
