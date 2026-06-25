from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
import os
import requests
import redis
import json
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables from .env file
# Must be called before accessing any env variables with os.getenv()
load_dotenv()

app = FastAPI()

# Read secrets from environment variables
API_KEY = os.getenv("WEATHER_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

# Create a single Redis connection at startup, reused for every request
r = redis.from_url(REDIS_URL)

# Rate limiter identifies users by their IP address
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter  # SlowAPI looks for the limiter here specifically

# Register the default handler so FastAPI returns a clean 429 JSON response
# when a user exceeds the rate limit
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/weather/{city}")
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
def get_weather(request: Request, city: str):
    # request: Request is required by SlowAPI to read the client's IP
    # city: str is a path parameter taken from the URL

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/forecast?locations={city}&aggregateHours=24&forecastDays=5&unitGroup=metric&shortColumnNames=false&contentType=json&key={API_KEY}"

    # Check Redis cache before calling the external API
    try:
        cached = r.get(city)  
    except Exception:
        cached = None  

    if cached is not None:
        # Data already exists in Redis, no need to call the API
        # json.loads converts the stored string back into a Python dictionary
        data = json.loads(cached)
    else:
        try:
            response = requests.get(url)
        except Exception:
            # Network error: couldn't reach the API at all
            raise HTTPException(
                status_code=500, detail="Cannot connect to weather API")

        # Handle specific HTTP error codes returned by Visual Crossing
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

        # Save result to Redis cache with 12-hour expiration (43200 seconds)
        # json.dumps converts the Python dictionary to a string for storage
        # Redis can only store strings, not Python objects
        r.set(city, json.dumps(data), ex=43200)

    # Extract today's weather from the response
    location_key = list(data["locations"].keys())[0]
    today = data["locations"][location_key]["values"][0]  # [0] = first day = today

    # Return only the fields we need, in a clean format
    return {
        "city": city,
        "temperature": today["temp"],      
        "humidity": today["humidity"],      
        "conditions": today["conditions"], 
        "min_temp": today["mint"],         
        "max_temp": today["maxt"],          
        "date": today["datetimeStr"]       
    }