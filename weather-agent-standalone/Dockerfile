# Weather Agent - Completely Standalone Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    httpx==0.25.1 \
    pydantic==2.5.0 \
    cryptography==41.0.7

# Create SDK inline
RUN mkdir -p /app/poros_sdk

# SDK __init__.py
RUN echo 'from .client import PorosClient' > /app/poros_sdk/__init__.py && \
    echo 'from .identity import generate_did, sign_agent_card' >> /app/poros_sdk/__init__.py && \
    echo '__version__ = "0.1.0"' >> /app/poros_sdk/__init__.py && \
    echo '__all__ = ["PorosClient", "generate_did", "sign_agent_card"]' >> /app/poros_sdk/__init__.py

# SDK identity.py (embedded)
RUN cat > /app/poros_sdk/identity.py << 'IDENTITY_EOF'
import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from typing import Tuple, Dict, Any

def generate_did() -> Tuple[str, str]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    public_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')
    did = f"did:poros:ed25519:{public_b64}"
    private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode('utf-8')
    return did, private_pem

def sign_agent_card(agent_card: Dict[str, Any], private_key_pem: str) -> str:
    canonical_json = json.dumps(agent_card, sort_keys=True, separators=(',', ':'))
    message = canonical_json.encode('utf-8')
    private_key = serialization.load_pem_private_key(private_key_pem.encode('utf-8'), password=None)
    signature = private_key.sign(message)
    return base64.b64encode(signature).decode('utf-8')
IDENTITY_EOF

# SDK client.py (embedded)
RUN cat > /app/poros_sdk/client.py << 'CLIENT_EOF'
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
            raise ValueError("Not authenticated")
        response = httpx.post(f"{self.backend_url}/api/registry/agents", headers={"Authorization": f"Bearer {self._token}"}, json={"agent_card": agent_card})
        response.raise_for_status()
        return response.json()
CLIENT_EOF

# Copy agent code (only file we need from repo)
COPY agent.py /app/agent.py

EXPOSE 9100

CMD ["python", "agent.py"]
