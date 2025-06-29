from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils.weather import get_weather_data

vibe_bp = Blueprint("vibe", __name__, url_prefix="/api")


@vibe_bp.route("/vibe-score/", methods=["GET"])
@login_required
def get_vibe_score():
    penalties = []
    score = 100

    # --- Location for weather API ---
    lat = request.args.get("lat", default=51.5074, type=float)  # Default: London
    lon = request.args.get("lon", default=-0.1278, type=float)
    weather = get_weather_data(lat, lon) or {}

    # --- User Data ---
    hrv = current_user.latest_hrv or 60
    rhr = current_user.latest_rhr or 55
    sleep = current_user.last_sleep_duration or 7.5
    mood = request.args.get("mood", "")  # e.g. 😐

    baseline_values = {
        "hrv": current_user.get_baseline("hrv") or 65,
        "rhr": current_user.get_baseline("rhr") or 54,
    }

    # --- Combined Data Point ---
    data_point = {
        "hrv": hrv,
        "rhr": rhr,
        "sleep": sleep,
        "dew_point": weather.get("dew_point", 12),
        "temperature": weather.get("temperature", 22),
        "humidity": weather.get("humidity", 50),
        "pressure": weather.get("pressure", 1015),
        "mood": mood,
    }

    # --- ENVIRONMENTAL ---
    if data_point["dew_point"] < 10 or data_point["dew_point"] > 20:
        score -= 2
        penalties.append("Suboptimal dew point")

    if data_point["pressure"] < 1005:
        score -= 2
        penalties.append("Low pressure = fatigue risk")
    elif data_point["pressure"] > 1035:
        score -= 1
        penalties.append("High pressure = tension")

    if data_point["temperature"] < 16:
        score -= 2
        penalties.append("Cold impairs focus")
    elif data_point["temperature"] > 27:
        score -= 2
        penalties.append("Overheating risk")

    if data_point["humidity"] < 30:
        score -= 1
        penalties.append("Dehydration risk")
    elif data_point["humidity"] > 70:
        score -= 2
        penalties.append("Sweat evaporation impacted")

    # --- SLEEP ---
    if data_point["sleep"] < 6:
        score -= 8
        penalties.append("Sleep debt")
    elif data_point["sleep"] > 9.5:
        score -= 3
        penalties.append("Possible oversleep")

    # --- BIO STATS ---
    hrv_dev = (data_point["hrv"] - baseline_values["hrv"]) / baseline_values["hrv"]
    if hrv_dev < -0.15:
        score -= 10
        penalties.append("HRV drop >15%: stress")
    elif hrv_dev < -0.07:
        score -= 5
        penalties.append("HRV drop >7%: early strain")
    elif hrv_dev > 0.25:
        score -= 4
        penalties.append("HRV spike: possible illness")

    rhr_dev = (data_point["rhr"] - baseline_values["rhr"]) / baseline_values["rhr"]
    if rhr_dev > 0.10:
        score -= 10
        penalties.append("RHR rise >10%: stress or illness")
    elif rhr_dev > 0.06:
        score -= 5
        penalties.append("RHR rise >6%: early strain")
    elif rhr_dev < -0.15:
        score -= 2
        penalties.append("Bradycardia/adaptation")

    # --- MOOD CHECK-IN ---
    if data_point["mood"] in ["😐", "😴", "😤"]:
        score -= 3
        penalties.append("Mood suggests strain or low energy")

    # --- FINAL OUTPUT ---
    score = max(score, 0)

    if score >= 90:
        zone = "Green"
        prompt = "You're primed for peak performance. Stack deep work or push physical goals."
    elif score >= 75:
        zone = "Yellow"
        prompt = "You're functional, but there’s some underlying strain. Buffer and monitor recovery."
    elif score >= 60:
        zone = "Orange"
        prompt = "You’re under strain. Today should prioritize recovery, light work, and recalibration."
    else:
        zone = "Red"
        prompt = "Recovery is compromised. Cancel unnecessary strain and restore your system aggressively."

    return jsonify(
        {
            "score": score,
            "zone": zone,
            "penalties": penalties,
            "prompt": prompt,
            "inputs": data_point,  # optional debug output
        }
    )
