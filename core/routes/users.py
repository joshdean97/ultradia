from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from ..models import User
from ..extensions import db

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


@users.route("/<user_id>", methods=["GET"])
def get_user_profile_by_id(user_id):
    """
    Retrieve a user profile by user ID.
    This endpoint should return user details such as name, email, and any other relevant information
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "peak_duration": user.peak_duration,
        "trough_duration": user.trough_duration,
        "grog_duration": user.morning_grog,
        "cycles_count": user.cycles,
        # Add any other user fields you want to expose
    }
    return jsonify(user_data), 200


@users.route("/<user_id>", methods=["PUT"])
@login_required
def update_user_profile(user_id):
    """
    Update the current user's profile.
    This endpoint should allow users to update their details such as name, email, and any other relevant information.
    """

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    user.email = data.get("email", user.email)
    user.name = data.get("name", user.name)
    user.peak_duration = data.get("peak_duration", user.peak_duration)
    user.trough_duration = data.get("trough_duration", user.trough_duration)
    user.morning_grog = data.get("morning_grog", user.morning_grog)
    user.cycles = data.get("cycles", user.cycles)
    # Save the updated user object to the database
    db.session.commit()

    return jsonify({"message": "User profile updated successfully"}), 200


@users.route("/<user_id>", methods=["DELETE"])
@login_required
def delete_user_profile(user_id):
    """
    Delete the current user's profile.
    This endpoint should allow users to delete their account.
    """
    if current_user.id != int(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User profile deleted successfully"}), 200
