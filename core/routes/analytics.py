from flask import Blueprint, request, jsonify
from ..models import AnalyticsEvent  # create this model
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..extensions import db

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/", methods=["POST"])
@jwt_required()
def log_event():
    data = request.get_json()
    event = data.get("event")
    meta = data.get("meta", {})
    user_id = get_jwt_identity()

    if not event:
        return jsonify({"error": "Missing event"}), 400

    db.session.add(
        AnalyticsEvent(
            user_id=user_id, event=event, meta=meta, timestamp=datetime.utcnow()
        )
    )
    db.session.commit()

    return jsonify({"message": "Event logged"}), 201
