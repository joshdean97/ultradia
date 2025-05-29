from flask import Blueprint, request, jsonify

from core.extensions import db
from core.models import User

auth = Blueprint("auth", __name__, url_prefix="/api/auth")

"""
Blueprint: /api/auth
This module handles user authentication, including login and registration.
Endpoints defined here are responsible for:
- User registration
- User login
- User logout
These endpoints are essential for managing user sessions and securing access to the application.
"""


@auth.route("/", methods=["GET"])
def auth_status():
    return jsonify({"endpoint": "auth"}), 200
