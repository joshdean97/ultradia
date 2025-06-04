from flask import Blueprint, request, jsonify
from datetime import datetime

from core.extensions import db
from core.models import UserDailyRecord

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


@records.route("/", methods=["GET"])
def records_status():
    return jsonify({"endpoint": "records"}), 200


@records.route("<user_id>/", methods=["POST"])
def create_record(user_id):
    """
    Creates a new daily record for a user.

    Args:
        user_id (int): The ID of the user for whom the record is being created.

    Returns:
        Response: A JSON response indicating success or failure, along with relevant data or error messages.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["date", "wake_time"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    hrv = data.get("hrv", None)
    date = data.get("date")
    formatted_date = datetime.strptime(date, "%Y-%m-%d").date() if date else None
    wake_time = data.get("wake_time")
    formatted_wake_time = (
        datetime.strptime(wake_time, "%H:%M:%S").time() if wake_time else None
    )
    user_id = user_id
    hrv = data.get("hrv", None)

    new_record = UserDailyRecord(
        user_id=user_id, date=formatted_date, wake_time=formatted_wake_time, hrv=hrv
    )
    db.session.add(new_record)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    sanitized_data = {
        key: data[key] for key in ["date", "wake_time", "hrv"] if key in data
    }
    return (
        jsonify({"message": "Record created successfully", "data": sanitized_data}),
        201,
    )


@records.route("<user_id>/", methods=["GET"])
def get_records(user_id):
    """
    Retrieves all daily records for a user.

    Args:
        user_id (int): The ID of the user whose records are being retrieved.

    Returns:
        Response: A JSON response containing the user's daily records or an error message.
    """
    records = UserDailyRecord.query.filter_by(user_id=user_id).all()
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


@records.route("<user_id>/<record_id>", methods=["GET"])
def get_record_by_id(user_id, record_id):
    """
    Retrieves a specific daily record by its ID for a user.

    Args:
        user_id (int): The ID of the user.
        record_id (int): The ID of the daily record.

    Returns:
        Response: A JSON response containing the record data or an error message.
    """
    record = UserDailyRecord.query.filter_by(user_id=user_id, id=record_id).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404

    record_data = {
        "id": record.id,
        "date": record.date.strftime("%Y-%m-%d"),
        "wake_time": record.wake_time.strftime("%H:%M:%S"),
        "hrv": record.hrv,
    }
    return jsonify({"record": record_data}), 200


@records.route("<user_id>/<record_id>", methods=["PUT"])
def update_record(user_id, record_id):
    """
    Updates a specific daily record by its ID for a user.

    Args:
        user_id (int): The ID of the user.
        record_id (int): The ID of the daily record.

    Returns:
        Response: A JSON response indicating success or failure, along with relevant data or error messages.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    record = UserDailyRecord.query.filter_by(user_id=user_id, id=record_id).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404

    if "date" in data:
        record.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
    if "wake_time" in data:
        record.wake_time = datetime.strptime(data["wake_time"], "%H:%M:%S").time()
    if "hrv" in data:
        record.hrv = data["hrv"]

    db.session.commit()
    return jsonify({"message": "Record updated successfully"}), 200


@records.route("<user_id>/<record_id>", methods=["DELETE"])
def delete_record(user_id, record_id):
    """
    Deletes a specific daily record by its ID for a user.

    Args:
        user_id (int): The ID of the user.
        record_id (int): The ID of the daily record.

    Returns:
        Response: A JSON response indicating success or failure.
    """
    record = UserDailyRecord.query.filter_by(user_id=user_id, id=record_id).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Record deleted successfully"}), 200
