# Weather Agent - Dockerfile for Railway deployment

FROM python:3.11-slim

WORKDIR /app

# Copy SDK (needed by agent)
COPY sdk/poros_sdk /app/poros_sdk

# Copy agent files
COPY agents/weather_agent/agent.py /app/agent.py

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic cryptography

# Railway provides PORT environment variable
ENV PORT=9100

# Expose port
EXPOSE 9100

# Run the agent
CMD python agent.py
