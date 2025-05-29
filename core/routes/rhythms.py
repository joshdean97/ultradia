from flask import Blueprint, request, jsonify

from core.extensions import db
from core.models import User

rhythms = Blueprint("rhythms", __name__, url_prefix="/api/rhythms")

"""
Blueprint: /api/rhythms
This module handles ultradian rhythm tracking, including wake time,
ultradian cycle configurations, and optional biometric data such as HRV (Heart Rate Variability).
Endpoints defined here are responsible for:
- Creating a new ultradian rhythm configuration
- Retrieving all configurations for a user
- Updating or deleting specific ultradian rhythm configurations
These configurations are used to personalize and optimize each user's ultradian rhythm tracking experience.
"""


@rhythms.route("/", methods=["GET"])
def rhythms_status():
    return jsonify({"endpoint": "rhythms"}), 200
