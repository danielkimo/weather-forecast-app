"""Simple weather web app.

- Geocoding: Nominatim (OpenStreetMap), which supports searching by city
  name in any language, including Chinese.
- Forecast: Open-Meteo's free, key-free forecast API.
"""
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Nominatim's usage policy requires an identifying User-Agent on requests.
GEOCODE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SimpleWeatherApp/1.0; "
    "+https://github.com/danielkimo/weather-forecast-app)"
}

# WMO weather codes -> human readable description + emoji icon.
WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


def describe_weather_code(code):
    return WEATHER_CODES.get(code, ("Unknown", "❔"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def api_weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Please provide a city name."}), 400

    try:
        geo_resp = requests.get(
            GEOCODE_URL,
            params={
                "q": city,
                "format": "json",
                "limit": 1,
                "accept-language": "zh-TW,en",
                "addressdetails": 1,
            },
            headers=GEOCODE_HEADERS,
            timeout=10,
        )
        geo_resp.raise_for_status()
        results = geo_resp.json()
    except requests.RequestException:
        return jsonify({"error": "Could not reach the geocoding service."}), 502

    if not results:
        return jsonify({"error": f'City "{city}" not found.'}), 404

    place = results[0]
    lat, lon = float(place["lat"]), float(place["lon"])
    address = place.get("address", {})
    place_name = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("county")
        or place.get("display_name", city).split(",")[0]
    )
    # Nominatim sometimes returns "simplified/traditional" combined names
    # (e.g. "东京都/東京都"); prefer the latter part for zh-TW display.
    if "/" in place_name:
        place_name = place_name.split("/")[-1]
    place_country = address.get("country")
    place_admin1 = address.get("state") or address.get("region")

    try:
        weather_resp = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                "timezone": "auto",
                "forecast_days": 5,
            },
            timeout=10,
        )
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()
    except requests.RequestException:
        return jsonify({"error": "Could not reach the weather service."}), 502

    current = weather_data.get("current", {})
    daily = weather_data.get("daily", {})

    current_desc, current_icon = describe_weather_code(current.get("weather_code"))

    forecast = []
    for i, date in enumerate(daily.get("time", [])):
        desc, icon = describe_weather_code(daily.get("weather_code", [None])[i])
        forecast.append(
            {
                "date": date,
                "max": daily.get("temperature_2m_max", [None])[i],
                "min": daily.get("temperature_2m_min", [None])[i],
                "description": desc,
                "icon": icon,
            }
        )

    return jsonify(
        {
            "location": {
                "name": place_name,
                "country": place_country,
                "admin1": place_admin1,
            },
            "current": {
                "temperature": current.get("temperature_2m"),
                "apparent_temperature": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "description": current_desc,
                "icon": current_icon,
            },
            "forecast": forecast,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)
