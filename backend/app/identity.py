"""
Poros Protocol - Identity & Cryptography Module

Handles DID generation, Ed25519 key management, and AgentCard signing/verification.
"""

import json
import base64
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


def generate_keypair() -> Tuple[str, str]:
    """
    Generate a new Ed25519 keypair.

    Returns:
        Tuple of (did, private_key_pem)
        - did: Poros DID in format "did:poros:ed25519:base64_public_key"
        - private_key_pem: PEM-encoded private key for storage
    """
    # Generate Ed25519 keypair
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Export public key as raw bytes
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    # Create DID from public key
    public_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')
    did = f"did:poros:ed25519:{public_b64}"

    # Export private key as PEM for storage
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    return did, private_pem


def sign_agent_card(agent_card_dict: dict, private_key_pem: str) -> str:
    """
    Sign an AgentCard with a private key.

    Args:
        agent_card_dict: AgentCard as dictionary (without 'signature' field)
        private_key_pem: PEM-encoded private key

    Returns:
        Base64-encoded signature
    """
    # Canonicalize the agent card (deterministic JSON)
    canonical_json = json.dumps(agent_card_dict, sort_keys=True, separators=(',', ':'))
    message = canonical_json.encode('utf-8')

    # Load private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None
    )

    # Sign the message
    signature = private_key.sign(message)

    # Return base64-encoded signature
    return base64.b64encode(signature).decode('utf-8')


def verify_agent_card(agent_card_dict: dict, signature_b64: str, did: str) -> bool:
    """
    Verify an AgentCard signature.

    Args:
        agent_card_dict: AgentCard as dictionary (without 'signature' field)
        signature_b64: Base64-encoded signature
        did: DID of the signer (must be did:poros:ed25519:...)

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Parse DID to extract public key
        if not did.startswith("did:poros:ed25519:"):
            return False

        public_key_b64 = did.split(":")[-1]

        # Add padding if needed
        padding = 4 - (len(public_key_b64) % 4)
        if padding != 4:
            public_key_b64 += '=' * padding

        public_bytes = base64.urlsafe_b64decode(public_key_b64)

        # Load public key
        public_key = Ed25519PublicKey.from_public_bytes(public_bytes)

        # Canonicalize the agent card
        canonical_json = json.dumps(agent_card_dict, sort_keys=True, separators=(',', ':'))
        message = canonical_json.encode('utf-8')

        # Decode signature
        signature = base64.b64decode(signature_b64)

        # Verify signature
        public_key.verify(signature, message)
        return True

    except InvalidSignature:
        return False
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False


def extract_public_key_from_did(did: str) -> str:
    """
    Extract the base64-encoded public key from a Poros DID.

    Args:
        did: Poros DID (did:poros:ed25519:...)

    Returns:
        Base64-encoded public key
    """
    if not did.startswith("did:poros:ed25519:"):
        raise ValueError("Invalid Poros DID format")

    return did.split(":")[-1]
