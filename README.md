# Weather API

A lightweight REST API that fetches and returns weather data from a third-party weather service. Built with FastAPI, it uses Redis caching to minimize external API calls and rate limiting to prevent abuse.

## Features

- **Real-time weather data** sourced from the [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api)
- **Redis caching** with a 12-hour expiration to reduce redundant API calls and improve response times
- **Rate limiting** of 10 requests per minute per client to protect the service from abuse
- **Robust error handling** that returns appropriate HTTP status codes for invalid cities, authentication failures, and upstream outages
- **Environment-based configuration** to keep API keys and connection strings out of the codebase

## Tech Stack

- **Python**
- **FastAPI** — web framework
- **Uvicorn** — ASGI server
- **Redis** — in-memory caching
- **SlowAPI** — rate limiting
- **Requests** — HTTP client for calling the external API

## Prerequisites

- Python 3.10 or higher
- A free [Visual Crossing API key](https://www.visualcrossing.com/weather-api)
- A Redis instance (local or hosted, e.g. [Redis Cloud](https://redis.io/try-free/))

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Henryquach12/Weather-API.git
   cd Weather-API
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root with the following variables:

```
WEATHER_API_KEY=your_visual_crossing_api_key
REDIS_URL=redis://:your_password@your_host:your_port
```

> **Note:** The `.env` file is excluded from version control via `.gitignore`. Never commit your API keys.

## Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive documentation (Swagger UI) is automatically available at `http://127.0.0.1:8000/docs`.

## Usage

### Get weather by city

```
GET /weather/{city}
```

**Example request:**

```
GET http://127.0.0.1:8000/weather/Hanoi
```

**Example response:**

```json
{
  "city": "Hanoi",
  "temperature": 32.1,
  "humidity": 78.4,
  "conditions": "Partly cloudy",
  "min_temp": 27.0,
  "max_temp": 35.5,
  "date": "2026-06-25T00:00:00+07:00"
}
```

## Error Responses

| Status Code | Meaning |
|-------------|---------|
| `400` | The provided city is not valid |
| `401` | Invalid API key |
| `429` | Rate limit exceeded (more than 10 requests per minute) |
| `500` | Could not connect to the weather service |
| `503` | The weather service is currently unavailable |

## How It Works

1. A request arrives at `/weather/{city}`.
2. The API checks Redis for cached data under the city key.
3. **Cache hit:** the cached result is returned immediately.
4. **Cache miss:** the API calls Visual Crossing, stores the result in Redis with a 12-hour expiration, and returns the data.

This approach keeps responses fast and stays well within the limits of the free Visual Crossing tier.

## Project Structure

```
Weather-API/
├── main.py            # Application entry point and route definitions
├── .env               # Environment variables (not committed)
├── .gitignore         # Files excluded from version control
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## Future Improvements

- Add support for multi-day and hourly forecasts
- Introduce API key authentication for end users
- Deploy to a cloud platform (Railway, Render, or a VPS)
- Add unit and integration tests

## License

This project is open source and available under the MIT License.
https://roadmap.sh/projects/weather-api-wrapper-service
