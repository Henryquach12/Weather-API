from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
API_KEY = os.getenv("WEATHER_API_KEY")
@app.get("/weather/{city}")
def get_weather(city: str):
    return {
        "city": city,
        "temperature": 32, 
        "humidity": 80,
        "conditions": "Partly cloudy"
    }