from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from core.extensions import db
from core.models import User

from authlib.integrations.flask_client import OAuth

import os

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

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo",
    client_kwargs={
        "scope": "email profile",  # 🔥 REMOVE openid
        "token_endpoint_auth_method": "client_secret_post",
    },
)


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


@auth.route("/login/google")
def login_google():
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth.route("/callback/google")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        print("✅ Token received:", token)
    except Exception as e:
        print("❌ Token exchange failed:", e)
        return jsonify({"error": "Token exchange failed", "details": str(e)}), 400

    try:
        resp = oauth.google.get("userinfo")
        print("📥 Userinfo response status:", resp.status_code)
        print("📥 Userinfo response text:", resp.text)
        user_info = resp.json()
    except Exception as e:
        print("❌ Failed to decode userinfo:", e)
        return (
            jsonify({"error": "Failed to fetch user info", "details": str(e)}),
            400,
        )  # 🔥 Don't call `parse_id_token(token)` anywhere

    # FIX: Only do this
    resp = oauth.google.get("userinfo")
    user_info = resp.json()

    email = user_info.get("email")
    name = user_info.get("name", "Google User")

    if not email:
        return jsonify({"error": "Failed to retrieve user info"}), 400

    # Get or create user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name, password_hash="oauth")  # placeholder
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return redirect(
        f"http://localhost:3000/auth/callback?token={access_token}&user_id={user.id}&name={user.name}"
    )
