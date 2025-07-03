from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from core.extensions import db
from core.models import User

auth = Blueprint("auth", __name__, url_prefix="/api/auth")

"""
Blueprint: /auth
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

    # add more complex validation as needed

    if not email or not password:
        return jsonify({"error": "Username and password are required"}), 400

    new_user = User(email=email, password_hash=password, name=name)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token, "user_id": user.id})
    else:
        return jsonify({"error": "Invalid credentials"}), 401
