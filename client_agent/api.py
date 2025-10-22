"""
FastAPI server for Intelligent Client Agent
Provides a chat API that the frontend can call
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from intelligent_client import IntelligentClient
import uvicorn

app = FastAPI(title="Poros Client Agent API")

# CORS - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store client instances per session (in production, use Redis/DB)
clients = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the intelligent client agent"""

    # Get or create client for this session
    if request.session_id not in clients:
        clients[request.session_id] = IntelligentClient()

    client = clients[request.session_id]

    # Process the message
    response = await client.process_message(request.message)

    return ChatResponse(
        response=response,
        session_id=request.session_id
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {
        "service": "Poros Intelligent Client Agent",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
