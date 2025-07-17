from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, AnalyticsEvent, UserDailyRecord, Leads
from ..extensions import db


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/", methods=["GET"])
@jwt_required()
def get_admin_overview():
    current_user = get_jwt_identity()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    user_count = User.query.count()
    record_count = UserDailyRecord.query.count()
    lead_count = Leads.query.count()

    return (
        jsonify({"users": user_count, "records": record_count, "leads": lead_count}),
        200,
    )


@admin_bp.route("/analytics", methods=["GET"])
@jwt_required()
def get_analytics_view():
    current_user = get_jwt_identity()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    events = (
        AnalyticsEvent.query.order_by(AnalyticsEvent.timestamp.desc()).limit(100).all()
    )
    return jsonify([e.to_dict() for e in events])


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def get_all_users():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    users = User.query.order_by(User.id.desc()).all()
    return jsonify(
        [
            {
                "id": u.id,
                "email": u.email,
                "is_admin": u.is_admin,
            }
            for u in users
        ]
    )


@admin_bp.route("/leads", methods=["GET"])
@jwt_required()
def get_all_leads():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    leads = Leads.query.order_by(Leads.id.desc()).all()
    return jsonify(
        [
            {
                "id": l.id,
                "email": l.email,
                "name": l.name,
                "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            }
            for l in leads
        ]
    )
