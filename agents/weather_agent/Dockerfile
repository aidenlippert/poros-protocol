# Weather Agent - Standalone Dockerfile for Railway

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (for layer caching)
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    httpx==0.25.1 \
    pydantic==2.5.0 \
    cryptography==41.0.7

# Copy the agent file
COPY agent.py /app/agent.py

# Copy SDK inline (create it in the image)
RUN mkdir -p /app/poros_sdk

# Create __init__.py
RUN echo 'from .client import PorosClient\nfrom .identity import generate_did, sign_agent_card\n\n__version__ = "0.1.0"\n__all__ = ["PorosClient", "generate_did", "sign_agent_card"]' > /app/poros_sdk/__init__.py

# Create identity.py (inline)
COPY <<'EOF' /app/poros_sdk/identity.py
import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from typing import Tuple, Dict, Any

def generate_did() -> Tuple[str, str]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')
    did = f"did:poros:ed25519:{public_b64}"
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    return did, private_pem

def sign_agent_card(agent_card: Dict[str, Any], private_key_pem: str) -> str:
    canonical_json = json.dumps(agent_card, sort_keys=True, separators=(',', ':'))
    message = canonical_json.encode('utf-8')
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None
    )
    signature = private_key.sign(message)
    return base64.b64encode(signature).decode('utf-8')
EOF

# Create client.py (inline)
COPY <<'EOF' /app/poros_sdk/client.py
import httpx
from typing import Dict, Any, Optional, List

class PorosClient:
    def __init__(self, backend_url: str = "https://poros-protocol-production.up.railway.app", username: Optional[str] = None, password: Optional[str] = None):
        self.backend_url = backend_url.rstrip('/')
        self.username = username
        self.password = password
        self._token: Optional[str] = None

    def register_user(self, username: str, email: str, password: str) -> str:
        response = httpx.post(f"{self.backend_url}/api/registry/users", json={"username": username, "email": email, "password": password})
        response.raise_for_status()
        data = response.json()
        self._token = data["access_token"]
        return self._token

    def register_agent(self, agent_card: Dict[str, Any]) -> Dict[str, Any]:
        if not self._token:
            raise ValueError("Not authenticated. Call register_user() first")
        response = httpx.post(f"{self.backend_url}/api/registry/agents", headers={"Authorization": f"Bearer {self._token}"}, json={"agent_card": agent_card})
        response.raise_for_status()
        return response.json()

    def discover_agents(self, capability: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        payload = {"capability": capability}
        if filters:
            payload["filters"] = filters
        response = httpx.post(f"{self.backend_url}/orchestrate/discover", json=payload)
        response.raise_for_status()
        return response.json()["agents"]

    def query_agent(self, agent_did: str, query: Dict[str, Any]) -> Dict[str, Any]:
        response = httpx.post(f"{self.backend_url}/orchestrate/query", json={"agent_did": agent_did, "query": query})
        response.raise_for_status()
        return response.json()
EOF

# Expose port
EXPOSE 9100

# Run the agent
CMD ["python", "agent.py"]
