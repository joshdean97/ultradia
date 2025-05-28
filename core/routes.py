from flask import Blueprint

cycle = Blueprint("session", __name__)


@cycle.route("/api/cycle", methods=["GET"])
def cycle_home():
    return {"message": "Welcome to the cycle API!"}, 200


@cycle.route("/api/create_cycle", methods=["POST"])
def create_cycle():
    # Logic to create a cycle
    return {"message": "Cycle created successfully"}, 201
