from flask import Blueprint, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    current_user,
)

vital = Blueprint("vital", __name__, url_prefix="/api/energy-potential")


@vital.route("/", methods=["GET"])
@jwt_required()
def get_energy_potential():
    result = current_user.calculate_vital_index()
    if not result:
        return (
            jsonify({"error": "Not enough HRV data to calculate energy potential"}),
            400,
        )
    return jsonify(result), 200
