import requests
from django.conf import settings
from django.core.cache import cache
from collections import defaultdict
from datetime import datetime

def get_weather_by_city(city):
    cache_key = f"weather_{city.lower()}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data  # Return cached weather
    
    api_key = settings.OPENWEATHER_API_KEY
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "icon": data["weather"][0]["icon"],
            "rainfall": data.get("rain", {}).get("1h", 0.0)
        }
    else:
        return {"error": response.json().get("message", "Failed to fetch weather")}


def get_forecast_by_city(city):
    api_key = settings.OPENWEATHER_API_KEY
    base_url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return {"error": response.json().get("message", "Failed to fetch forecast")}

    data = response.json()
    forecast_by_day = defaultdict(list)

    for entry in data["list"]:
        date = entry["dt_txt"].split(" ")[0]
        forecast_by_day[date].append({
            "time": entry["dt_txt"],
            "temp": entry["main"]["temp"],
            "description": entry["weather"][0]["description"],
            "humidity": entry["main"]["humidity"],
            "wind_speed": entry["wind"]["speed"],
            "rainfall": entry.get("rain", {}).get("3h", 0.0),
            "icon": entry["weather"][0]["icon"],
        })


    # Aggregate daily forecasts
    summarized_forecast = []
    for date, forecasts in forecast_by_day.items():
        avg_temp = sum(f["temp"] for f in forecasts) / len(forecasts)
        avg_humidity = sum(f["humidity"] for f in forecasts) / len(forecasts)
        total_rainfall = sum(f["rainfall"] for f in forecasts)
        common_description = max(set(f["description"] for f in forecasts), key=lambda x: [f["description"] for f in forecasts].count(x))
        summarized_forecast.append({
            "date": date,
            "average_temperature": round(avg_temp, 1),
            "average_humidity": round(avg_humidity, 1),
            "total_rainfall": round(total_rainfall, 1),
            "description": common_description,
            "icon": forecasts[0]["icon"]
        })

    return summarized_forecast


def get_forecast_average_by_city(city):
    """
    Returns average temperature, humidity, and total rainfall for the next 5 days (every 3 hours).
    """
    api_key = settings.OPENWEATHER_API_KEY
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return {"error": response.json().get("message", "Forecast data not found")}

    data = response.json()
    temps, humidities, rainfalls = [], [], []

    for entry in data["list"]:
        temps.append(entry["main"]["temp"])
        humidities.append(entry["main"]["humidity"])
        rainfalls.append(entry.get("rain", {}).get("3h", 0.0))

    return {
        "temperature": sum(temps) / len(temps),
        "humidity": sum(humidities) / len(humidities),
        "rainfall": sum(rainfalls)  # Total over 5 days
    }

