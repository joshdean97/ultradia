from flask import Blueprint

from datetime import datetime, timedelta

cycle = Blueprint("session", __name__)


@cycle.route("/api/cycle", methods=["GET"])
def cycle_home():
    return {"message": "Welcome to the cycle API!"}, 200


@cycle.route("/api/create_cycle", methods=["POST"])
def create_cycle():

    return {"message": "Cycle created successfully"}, 201
