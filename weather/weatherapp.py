from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv

app = Flask(__name__)

def get_weather_city(city):
    tomorrow_api_key = os.getenv("TOMORROW_API_KEY")
    geocode_api_key = os.getenv("GEOCODE_API_KEY")
    
    tomorrow_url = "https://api.tomorrow.io/v4/timelines"
    geocode_url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={geocode_api_key}"

    geocode_response = requests.get(geocode_url)

    if geocode_response.status_code == 200:
        location = geocode_response.json()['results'][0]['geometry']
        latitude = location['lat']
        longitude = location['lng']
    else:
        return f"Error geocoding city: {geocode_response.status_code}"

    start_time = datetime.utcnow().isoformat()+"Z"
    end_time = (datetime.utcnow() + timedelta(hours=24)).isoformat()+"Z"

    params = {
        "apikey": tomorrow_api_key,
        "location": f"{latitude},{longitude}",
        "fields": ["temperature", "precipitationProbability"],
        "timesteps": "1h",
        "units": "metric",
        "startTime": start_time,
        "endTime": end_time
    }

    response = requests.get(tomorrow_url, params=params)

    if response.status_code == 200:
        data = response.json()
        interval = data['data']['timelines'][0]['intervals'][0]
        temperature_celsius = interval['values']['temperature']
        temperature_fahrenheit = (temperature_celsius * 9/5) + 32
        return f"The temperature in {city} is {round(temperature_fahrenheit)} °F ({round(temperature_celsius)}°C)"
    else:
        return f"Error fetching weather data: {response.status_code}"

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    if request.method == "POST":
        city = request.form.get("city")
        weather = get_weather_city(city)
    
    return render_template("index.html", weather=weather)

if __name__ == "__main__":
    app.run(debug=True)