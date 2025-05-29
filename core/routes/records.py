from flask import Blueprint, request, jsonify

from core.extensions import db
from core.models import User

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


@records.route("/", methods=["GET"])
def records_status():
    return jsonify({"endpoint": "records"}), 200


@records.route("/create", methods=["POST"])
def create_record():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # add create logic here

    return jsonify({"message": "Record created successfully", "data": data}), 201
