"""
Weather Agent - Production Poros Agent

Provides real-time weather information using OpenWeatherMap API.
Built with the Poros SDK - demonstrates best practices.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'sdk'))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import uvicorn

from poros_sdk import PorosClient, generate_did, sign_agent_card

# ============================================
# CONFIGURATION
# ============================================

AGENT_NAME = "Poros Weather Service"
AGENT_DESCRIPTION = "Real-time weather information and 5-day forecasts for any city worldwide"
AGENT_PORT = int(os.getenv("PORT", "9100"))
AGENT_URL = os.getenv("AGENT_URL", "http://localhost:9100")  # Set via Railway env var

# OpenWeatherMap API (free tier: 60 calls/minute, 1000 calls/day)
# Get your free API key at: https://openweathermap.org/api
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo")  # Use "demo" for testing
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Poros capability
CAPABILITY = "weather_forecast"

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title=AGENT_NAME,
    description=AGENT_DESCRIPTION,
    version="1.0.0"
)

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class QueryRequest(BaseModel):
    action: str
    parameters: Dict[str, Any]


class QueryResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================
# WEATHER API INTEGRATION
# ============================================

async def get_current_weather(city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current weather for a city using OpenWeatherMap API.

    Args:
        city: City name
        country_code: Optional ISO 3166 country code (e.g., "US", "GB")

    Returns:
        Weather data dictionary
    """
    location = f"{city},{country_code}" if country_code else city

    # Use demo data if no API key
    if OPENWEATHER_API_KEY == "demo":
        return {
            "location": city,
            "temperature": 72,
            "feels_like": 70,
            "condition": "Partly Cloudy",
            "humidity": 65,
            "wind_speed": 8,
            "description": "Demo data - set OPENWEATHER_API_KEY env var for real data"
        }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPENWEATHER_BASE_URL}/weather",
                params={
                    "q": location,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "imperial"  # Fahrenheit
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            return {
                "location": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "pressure": data["main"]["pressure"]
            }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Weather API error: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather: {str(e)}")


async def get_forecast(city: str, days: int = 5) -> Dict[str, Any]:
    """
    Get weather forecast for a city.

    Args:
        city: City name
        days: Number of days (max 5 for free tier)

    Returns:
        Forecast data dictionary
    """
    # Use demo data if no API key
    if OPENWEATHER_API_KEY == "demo":
        return {
            "location": city,
            "forecast": [
                {"date": "2025-10-23", "temp_high": 75, "temp_low": 58, "condition": "Sunny"},
                {"date": "2025-10-24", "temp_high": 73, "temp_low": 60, "condition": "Cloudy"},
                {"date": "2025-10-25", "temp_high": 70, "temp_low": 55, "condition": "Rainy"},
            ],
            "note": "Demo data - set OPENWEATHER_API_KEY for real forecasts"
        }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OPENWEATHER_BASE_URL}/forecast",
                params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "imperial",
                    "cnt": min(days * 8, 40)  # API returns 3-hour intervals
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            # Group by date
            daily_forecast = {}
            for item in data["list"]:
                date = item["dt_txt"].split()[0]
                if date not in daily_forecast:
                    daily_forecast[date] = {
                        "date": date,
                        "temps": [],
                        "conditions": []
                    }
                daily_forecast[date]["temps"].append(item["main"]["temp"])
                daily_forecast[date]["conditions"].append(item["weather"][0]["main"])

            # Aggregate
            forecast = []
            for date_data in list(daily_forecast.values())[:days]:
                forecast.append({
                    "date": date_data["date"],
                    "temp_high": max(date_data["temps"]),
                    "temp_low": min(date_data["temps"]),
                    "condition": max(set(date_data["conditions"]), key=date_data["conditions"].count)
                })

            return {
                "location": data["city"]["name"],
                "country": data["city"]["country"],
                "forecast": forecast
            }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Weather API error: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecast: {str(e)}")


# ============================================
# POROS PROTOCOL ENDPOINTS
# ============================================

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Handle QUERY requests from the Poros orchestrator.

    Supported actions:
    - get_weather: Get current weather for a city
    - get_forecast: Get 5-day forecast for a city
    """
    try:
        if request.action == "get_weather":
            city = request.parameters.get("city")
            if not city:
                return QueryResponse(
                    status="error",
                    error="Missing required parameter: city"
                )

            country_code = request.parameters.get("country_code")
            weather_data = await get_current_weather(city, country_code)

            return QueryResponse(
                status="success",
                result=weather_data
            )

        elif request.action == "get_forecast":
            city = request.parameters.get("city")
            if not city:
                return QueryResponse(
                    status="error",
                    error="Missing required parameter: city"
                )

            days = request.parameters.get("days", 5)
            forecast_data = await get_forecast(city, days)

            return QueryResponse(
                status="success",
                result=forecast_data
            )

        else:
            return QueryResponse(
                status="error",
                error=f"Unknown action: {request.action}. Supported: get_weather, get_forecast"
            )

    except HTTPException as e:
        return QueryResponse(
            status="error",
            error=e.detail
        )
    except Exception as e:
        return QueryResponse(
            status="error",
            error=f"Internal error: {str(e)}"
        )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": AGENT_NAME,
        "capabilities": [CAPABILITY],
        "api_key_configured": OPENWEATHER_API_KEY != "demo"
    }


# ============================================
# REGISTRATION
# ============================================

def register_with_poros():
    """Register this agent with the Poros network."""

    print(f"\n{'='*60}")
    print(f"Registering {AGENT_NAME} with Poros Protocol")
    print(f"{'='*60}\n")

    client = PorosClient()

    # Step 1: Register/login user
    print("Step 1: Authenticating...")
    username = "weather_service"
    try:
        token = client.register_user(username, f"{username}@poros.com", "secure_pass_123")
        print(f"[OK] Authenticated as {username}\n")
    except Exception as e:
        print(f"[INFO] User exists, that's fine: {e}\n")
        return False

    # Step 2: Generate DID
    print("Step 2: Generating cryptographic identity...")
    did, private_key = generate_did()
    print(f"[OK] DID: {did}\n")

    # Step 3: Create AgentCard
    print("Step 3: Creating AgentCard...")
    agent_card = {
        "version": "2.0",
        "did": did,
        "name": AGENT_NAME,
        "description": AGENT_DESCRIPTION,
        "url": AGENT_URL,
        "capabilities": [
            {
                "name": CAPABILITY,
                "verbs": ["query"],
                "description": "Get weather and forecasts",
                "actions": ["get_weather", "get_forecast"]
            }
        ],
        "skills": [
            {
                "id": CAPABILITY,
                "name": "Weather Information",
                "description": "Real-time weather data and forecasts",
                "tags": ["weather", "forecast", "temperature", "conditions"]
            }
        ],
        "pricing": {
            "model": "free",
            "amount": 0,
            "currency": "USD"
        },
        "metadata": {
            "category": "information",
            "data_source": "OpenWeatherMap",
            "coverage": "worldwide",
            "response_time_ms": 200
        }
    }

    # Step 4: Sign AgentCard
    print("Step 4: Signing AgentCard...")
    signature = sign_agent_card(agent_card, private_key)
    agent_card["signature"] = signature
    print(f"[OK] Signed\n")

    # Step 5: Register
    print("Step 5: Registering with Poros network...")
    try:
        result = client.register_agent(agent_card)
        print(f"[SUCCESS] Agent registered!")
        print(f"  Agent ID: {result['agent_id']}")
        print(f"  DID: {result.get('did', 'N/A')}")
        print(f"  Status: Active\n")
        return True
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}\n")
        return False


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    # Register first
    if register_with_poros():
        print(f"{'='*60}")
        print(f"{AGENT_NAME} is live!")
        print(f"Listening on: {AGENT_URL}")
        print(f"{'='*60}\n")

        # Start server
        uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
