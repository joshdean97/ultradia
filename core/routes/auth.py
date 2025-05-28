from flask import Blueprint, request, jsonify

from core.extensions import db
from core.models import User

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.route("/", methods=["GET"])
def auth_status():
    return jsonify({"endpoint": "auth"}), 200
