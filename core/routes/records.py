from flask import Blueprint, request, jsonify

from core.extensions import db
from core.models import User

records = Blueprint("records", __name__, url_prefix="/api/records")


@records.route("/", methods=["GET"])
def records_status():
    return jsonify({"endpoint": "records"}), 200
