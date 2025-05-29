from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from ..models import User

users = Blueprint("users", __name__, url_prefix="/api/users")
"""
Blueprint: /api/users
This module handles user management, including user profile retrieval and updates.
Endpoints defined here are responsible for:
- Retrieving user profiles
- Updating user profiles
These endpoints are essential for managing user information and preferences.
"""


@users.route("/", methods=["GET"])
def users_status():
    return {"endpoint": "users"}, 200


@users.route("/me", methods=["GET"])
@login_required
def get_user_profile():
    """
    Retrieve the current user's profile.
    This endpoint should return user details such as name, email, and any other relevant information.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401

    # mock data for demonstration purposes
    # In a real application, you would retrieve the user data from the database
    # current_user = {
    #     "id": 1,
    #     "email": "test@gmail.com",
    #     "name": "Test User",
    #     "peak_duration": 90,
    #     "trough_duration": 20,
    #     "grog_duration": 20,
    #     "cycles_count": 5,
    # }

    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "peak_duration": current_user.peak_duration,
        "trough_duration": current_user.trough_duration,
        "grog_duration": current_user.morning_grog,
        "cycles_count": current_user.cycles,
        # Add any other user fields you want to expose
    }
    return jsonify(user_data), 200
