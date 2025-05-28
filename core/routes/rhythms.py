from flask import Blueprint, request, jsonify

from core.extensions import db
from core.models import User

rhythms = Blueprint("rhythms", __name__, url_prefix="/api/rhythms")


@rhythms.route("/", methods=["GET"])
def rhythms_status():
    return jsonify({"endpoint": "rhythms"}), 200
