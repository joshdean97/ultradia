# utils/weather.py
import requests


def get_weather_data(lat: float, lon: float):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,dew_point_2m,relative_humidity_2m,pressure_msl"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        return {
            "temperature": current.get("temperature_2m"),
            "dew_point": current.get("dew_point_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "pressure": current.get("pressure_msl"),
        }

    except Exception as e:
        print(f"Failed to fetch weather: {e}")
        return None
