from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

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


@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    password = generate_password_hash(data.get("password"))
    name = data.get("name", "User")

    if not email or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Here you would typically hash the password and save the user to the database
    new_user = User(email=email, password_hash=password, name=name)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201
