"""
Identity utilities - DID generation and AgentCard signing
"""

import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from typing import Tuple, Dict, Any


def generate_did() -> Tuple[str, str]:
    """
    Generate a new Ed25519 keypair and DID.

    Returns:
        Tuple of (did, private_key_pem)
    """
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
    """
    Sign an AgentCard with a private key.

    Args:
        agent_card: AgentCard as dictionary (without 'signature' field)
        private_key_pem: PEM-encoded private key

    Returns:
        Base64-encoded signature
    """
    canonical_json = json.dumps(agent_card, sort_keys=True, separators=(',', ':'))
    message = canonical_json.encode('utf-8')

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None
    )

    signature = private_key.sign(message)
    return base64.b64encode(signature).decode('utf-8')
