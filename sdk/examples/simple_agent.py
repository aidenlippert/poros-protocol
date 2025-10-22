"""
Simple Example Agent using Poros SDK

This example shows how to:
1. Register as a user
2. Create and register an agent
3. Run a simple FastAPI server that responds to queries
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from pydantic import BaseModel
from poros_sdk import PorosClient, generate_did, sign_agent_card
import uvicorn

# ============================================
# CONFIGURATION
# ============================================

AGENT_NAME = "Weather Bot"
AGENT_DESCRIPTION = "Provides weather information for any city"
AGENT_PORT = 8001
AGENT_URL = f"http://localhost:{AGENT_PORT}"  # Change to your public URL for production

# Capability your agent provides
CAPABILITY = "weather"

# ============================================
# AGENT LOGIC
# ============================================

app = FastAPI(title=AGENT_NAME)

class QueryRequest(BaseModel):
    action: str
    parameters: dict

class QueryResponse(BaseModel):
    result: dict
    signature: str = None


@app.post("/query")
async def handle_query(request: QueryRequest):
    """
    Handle QUERY requests from the Poros orchestrator.

    In production, you would:
    1. Verify the request signature
    2. Process the query
    3. Sign your response
    """
    if request.action == "get_weather":
        city = request.parameters.get("city", "Unknown")

        # Mock weather data (replace with real API call)
        weather_data = {
            "city": city,
            "temperature": 72,
            "condition": "Sunny",
            "humidity": 45
        }

        return QueryResponse(result=weather_data)

    else:
        return {"error": f"Unknown action: {request.action}"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ============================================
# REGISTRATION
# ============================================

def register_agent():
    """Register this agent with the Poros network."""

    print(f"\n{'='*60}")
    print(f"Registering {AGENT_NAME} with Poros Protocol")
    print(f"{'='*60}\n")

    # Initialize client
    client = PorosClient()

    # Step 1: Register as a user (or login)
    print("Step 1: Creating user account...")
    try:
        token = client.register_user(
            username="weather_owner_6567",
            email="weather@example.com",
            password="secure_password_123"
        )
        print(f"[OK] User registered! Token: {token[:20]}...\n")
    except Exception as e:
        print(f"Registration failed: {e}")
        return False
