# Weather Agent

**Production-ready Poros agent providing real-time weather information.**

Built with the Poros SDK as a reference implementation showing best practices for agent development.

## Features

- Real-time weather for any city worldwide
- 5-day weather forecasts
- Powered by OpenWeatherMap API
- Demo mode (works without API key)
- Production-ready error handling
- Clean, documented code

## Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn httpx pydantic

# Run with demo data (no API key needed)
cd agents/weather_agent
python agent.py
```

The agent will:
1. Register with the Poros network
2. Start listening on port 9100
3. Be discoverable via the DISCOVER endpoint

## Using a Real Weather API

Get a free API key from [OpenWeatherMap](https://openweathermap.org/api):

```bash
# Set your API key
export OPENWEATHER_API_KEY="your_key_here"

# Run the agent
python agent.py
```

## Supported Actions

### `get_weather`

Get current weather for a city.

**Request:**
```json
{
  "action": "get_weather",
  "parameters": {
    "city": "San Francisco",
    "country_code": "US"  // optional
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "location": "San Francisco",
    "country": "US",
    "temperature": 62,
    "feels_like": 60,
    "condition": "Clear",
    "description": "clear sky",
    "humidity": 72,
    "wind_speed": 8.5,
    "pressure": 1015
  }
}
```

### `get_forecast`

Get weather forecast for a city.

**Request:**
```json
{
  "action": "get_forecast",
  "parameters": {
    "city": "London",
    "days": 5  // optional, defaults to 5
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "location": "London",
    "country": "GB",
    "forecast": [
      {
        "date": "2025-10-23",
        "temp_high": 58,
        "temp_low": 45,
        "condition": "Rain"
      },
      // ... more days
    ]
  }
}
```

## Testing the Agent

```bash
# Health check
curl http://localhost:9100/health

# Query weather
curl -X POST http://localhost:9100/query \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_weather",
    "parameters": {"city": "Tokyo"}
  }'
```

## Discovering via Poros

```python
from poros_sdk import PorosClient

client = PorosClient()

# Find weather agents
agents = client.discover_agents("weather_forecast")
print(agents)

# Query the agent
response = client.query_agent(
    agent_did=agents[0]["did"],
    query={
        "action": "get_weather",
        "parameters": {"city": "Paris"}
    }
)
print(response)
```

## Architecture

This agent demonstrates:

- **Clean separation**: Weather API logic separate from Poros protocol handling
- **Error handling**: Graceful degradation and clear error messages
- **Demo mode**: Works without external dependencies for testing
- **Type safety**: Pydantic models for all requests/responses
- **Production ready**: Proper logging, health checks, and documentation

## Deployment

For production deployment:

1. Set `AGENT_URL` to your public URL
2. Set `OPENWEATHER_API_KEY` environment variable
3. Deploy to your hosting platform (Railway, Heroku, etc.)
4. Agent will auto-register with Poros on startup

## License

MIT
