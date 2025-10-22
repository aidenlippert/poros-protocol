# Weather Agent - Standalone Dockerfile for Railway
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    httpx==0.25.1 \
    pydantic==2.5.0 \
    cryptography==41.0.7

# Create poros_sdk directory
RUN mkdir -p /app/poros_sdk

# Create SDK files using echo (compatible with all Docker builders)
RUN echo "from .client import PorosClient" > /app/poros_sdk/__init__.py && \
    echo "from .identity import generate_did, sign_agent_card" >> /app/poros_sdk/__init__.py && \
    echo "__version__ = '0.1.0'" >> /app/poros_sdk/__init__.py && \
    echo "__all__ = ['PorosClient', 'generate_did', 'sign_agent_card']" >> /app/poros_sdk/__init__.py

# Create identity.py
RUN printf 'import json\nimport base64\nfrom cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey\nfrom cryptography.hazmat.primitives import serialization\nfrom typing import Tuple, Dict, Any\n\ndef generate_did() -> Tuple[str, str]:\n    private_key = Ed25519PrivateKey.generate()\n    public_key = private_key.public_key()\n    public_bytes = public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)\n    public_b64 = base64.urlsafe_b64encode(public_bytes).decode("utf-8").rstrip("=")\n    did = f"did:poros:ed25519:{public_b64}"\n    private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode("utf-8")\n    return did, private_pem\n\ndef sign_agent_card(agent_card: Dict[str, Any], private_key_pem: str) -> str:\n    canonical_json = json.dumps(agent_card, sort_keys=True, separators=(",", ":"))\n    message = canonical_json.encode("utf-8")\n    private_key = serialization.load_pem_private_key(private_key_pem.encode("utf-8"), password=None)\n    signature = private_key.sign(message)\n    return base64.b64encode(signature).decode("utf-8")\n' > /app/poros_sdk/identity.py

# Create client.py
RUN printf 'import httpx\nfrom typing import Dict, Any, Optional, List\n\nclass PorosClient:\n    def __init__(self, backend_url: str = "https://poros-protocol-production.up.railway.app", username: Optional[str] = None, password: Optional[str] = None):\n        self.backend_url = backend_url.rstrip("/")\n        self.username = username\n        self.password = password\n        self._token: Optional[str] = None\n\n    def register_user(self, username: str, email: str, password: str) -> str:\n        response = httpx.post(f"{self.backend_url}/api/registry/users", json={"username": username, "email": email, "password": password})\n        response.raise_for_status()\n        data = response.json()\n        self._token = data["access_token"]\n        return self._token\n\n    def register_agent(self, agent_card: Dict[str, Any]) -> Dict[str, Any]:\n        if not self._token:\n            raise ValueError("Not authenticated")\n        response = httpx.post(f"{self.backend_url}/api/registry/agents", headers={"Authorization": f"Bearer {self._token}"}, json={"agent_card": agent_card})\n        response.raise_for_status()\n        return response.json()\n' > /app/poros_sdk/client.py

# Copy agent code
COPY agent.py /app/agent.py

EXPOSE 9100

CMD ["python", "agent.py"]
