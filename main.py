from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import requests
import redis
import json

load_dotenv()
app = FastAPI()
API_KEY = os.getenv("WEATHER_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

r = redis.from_url(REDIS_URL)
@app.get("/weather/{city}")
def get_weather(city: str):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/forecast?locations={city},VA,20170&aggregateHours=24&forecastDays=5&unitGroup=us&shortColumnNames=false&contentType=json&key={API_KEY}"
    try:
        cached = r.get(city)
    except Exception:
        cached = None

    if cached is not None:
        data = json.loads(cached)
    else:
        try:
            response = requests.get(url)
        except Exception:
            raise HTTPException(
                status_code=500, detail="Cannot connect to weather API")

        if response.status_code == 400:
            raise HTTPException(status_code=400, detail="City is not valid")
        elif response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid API key")
        elif response.status_code == 429:
            raise HTTPException(status_code=429, detail="Too many requests")
        elif response.status_code >= 500:
            raise HTTPException(
                status_code=503, detail="Weather API is unavailable")

        data = response.json()
        r.set(city, json.dumps(data), ex=43200)

    location_key = list(data["locations"].keys())[0]
    today = data["locations"][location_key]["values"][0]
    return {
        "city": city,
        "temperature": today["temp"],
        "humidity": today["humidity"],
        "conditions": today["conditions"],
        "min_temp": today["mint"],
        "max_temp": today["maxt"],
        "date": today["datetimeStr"]
    }
