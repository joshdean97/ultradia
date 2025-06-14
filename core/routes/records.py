from flask import Blueprint, request, jsonify, redirect, url_for
from datetime import datetime

from flask_login import login_required, current_user

from core.extensions import db
from core.models import UserDailyRecord

from datetime import date

records = Blueprint("records", __name__, url_prefix="/api/records")

"""
Blueprint: /api/records

This module handles user daily records, including wake time, 
ultradian cycle configurations, and optional biometric data 
such as HRV (Heart Rate Variability).

Endpoints defined here are responsible for:
- Creating a new daily record
- Retrieving all records for a user
- Updating or deleting specific daily records

These records are used to personalize and optimize each user's 
ultradian rhythm tracking experience.
"""
"""
MODEL:
class UserDailyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    wake_time = db.Column(db.Time, nullable=False)
    hrv = db.Column(db.Float)  # Optional for biometrics


"""


@records.route("/", methods=["POST"])
@login_required
def create_record():
    """
    Creates a new daily record for a user.

    Returns:
        Response: A JSON response indicating success or failure, along with relevant data or error messages.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["wake_time"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    hrv = data.get("hrv", None)
    date = datetime.now().date()  # Use current date for the record
    wake_time = data.get("wake_time")
    formatted_wake_time = datetime.strptime(wake_time, "%H:%M").time()

    user_id = current_user.id

    new_record = UserDailyRecord(
        user_id=user_id, date=date, wake_time=formatted_wake_time, hrv=hrv
    )
    db.session.add(new_record)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return (
        jsonify({"message": "Record created successfully", "record_id": new_record.id}),
        201,
    )


@records.route("/", methods=["GET"])
@login_required
def get_records():
    """
    Retrieves all daily records for a user.

    Returns:
        Response: A JSON response containing the user's daily records or an error message.
    """
    records = UserDailyRecord.query.filter_by(user_id=current_user.id).all()
    if not records:
        return jsonify({"message": "No records found"}), 404

    records_data = [
        {
            "id": record.id,
            "date": record.date.strftime("%Y-%m-%d"),
            "wake_time": record.wake_time.strftime("%H:%M:%S"),
            "hrv": record.hrv,
        }
        for record in records
    ]
    return jsonify({"records": records_data}), 200


@records.route("/<record_id>/", methods=["GET"])
def get_record_by_id(record_id):
    """
    Retrieves a specific daily record by its ID for a user.

    Args:
        record_id (int): The ID of the daily record.

    Returns:
        Response: A JSON response containing the record data or an error message.
    """
    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, id=record_id
    ).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404

    record_data = {
        "id": record.id,
        "date": record.date.strftime("%Y-%m-%d"),
        "wake_time": record.wake_time.strftime("%H:%M:%S"),
        "hrv": record.hrv,
    }
    return jsonify({"record": record_data}), 200


@records.route("/<int:record_id>/", methods=["PUT", "OPTIONS"])
@login_required
def update_record(record_id):
    record = UserDailyRecord.query.get(record_id)

    if not record or record.user_id != current_user.id:
        return jsonify({"error": "Record not found or unauthorized"}), 404

    data = request.get_json()
    if "wake_time" in data:
        from datetime import datetime

        try:
            record.wake_time = datetime.strptime(data["wake_time"], "%H:%M:%S").time()
        except ValueError:
            record.wake_time = datetime.strptime(data["wake_time"], "%H:%M").time()

    if "hrv" in data:
        record.hrv = data["hrv"]

    db.session.commit()
    return jsonify({"message": "Record updated"}), 200


@records.route("/<record_id>/", methods=["DELETE"])
@login_required
def delete_record(record_id):
    """
    Deletes a specific daily record by its ID for a user.

    Args:
        user_id (int): The ID of the user.
        record_id (int): The ID of the daily record.

    Returns:
        Response: A JSON response indicating success or failure.
    """
    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, id=record_id
    ).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404

    db.session.delete(record)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Record deleted successfully"}), 200


@records.route("/today/", methods=["GET"])
@login_required
def get_today_record():
    today = date.today()
    record = UserDailyRecord.query.filter_by(
        user_id=current_user.id, date=today
    ).first()
    if record:
        return (
            jsonify(
                {
                    "id": record.id,
                    "wake_time": record.wake_time.strftime("%H:%M:%S"),
                    "hrv": record.hrv,
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "No record found"}), 404
