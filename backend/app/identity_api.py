"""
Poros Protocol - Identity API Endpoints

Handles DID generation and AgentCard signing for agent developers.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from . import identity

router = APIRouter(prefix="/api/identity", tags=["Identity & DIDs"])


class GenerateDIDResponse(BaseModel):
    did: str
    private_key_pem: str
    message: str


class SignAgentCardRequest(BaseModel):
    agent_card: Dict[str, Any]
    private_key_pem: str


class SignAgentCardResponse(BaseModel):
    signature: str
    signed_agent_card: Dict[str, Any]


class VerifyAgentCardRequest(BaseModel):
    agent_card: Dict[str, Any]
    signature: str
    did: str


class VerifyAgentCardResponse(BaseModel):
    valid: bool
    message: str


@router.post("/generate-did", response_model=GenerateDIDResponse)
async def generate_did():
    """
    Generate a new Ed25519 keypair and DID for an agent.

    Returns:
        - did: Poros DID (did:poros:ed25519:...)
        - private_key_pem: Private key in PEM format (KEEP THIS SECRET!)

    WARNING: The private key should be stored securely by the agent owner.
    It will be needed to sign AgentCards and prove ownership.
    """
    did, private_key_pem = identity.generate_keypair()

    return GenerateDIDResponse(
        did=did,
        private_key_pem=private_key_pem,
        message="DID generated successfully. IMPORTANT: Store the private_key_pem securely - you'll need it to sign your AgentCard."
    )


@router.post("/sign-agent-card", response_model=SignAgentCardResponse)
async def sign_agent_card(request: SignAgentCardRequest):
    """
    Sign an AgentCard with a private key.

    The signature proves that the agent owner controls the DID and that
    the AgentCard hasn't been tampered with.
    """
    try:
        # Remove signature field if it exists (we're about to create it)
        agent_card_unsigned = {k: v for k, v in request.agent_card.items() if k != 'signature'}

        # Sign the agent card
        signature = identity.sign_agent_card(agent_card_unsigned, request.private_key_pem)

        # Add signature to the agent card
        signed_card = {**agent_card_unsigned, "signature": signature}

        return SignAgentCardResponse(
            signature=signature,
            signed_agent_card=signed_card
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to sign AgentCard: {str(e)}")


@router.post("/verify-agent-card", response_model=VerifyAgentCardResponse)
async def verify_agent_card(request: VerifyAgentCardRequest):
    """
    Verify an AgentCard signature.

    This checks that:
    1. The signature was created by the private key corresponding to the DID
    2. The AgentCard data hasn't been modified since signing
    """
    # Remove signature from agent card for verification
    agent_card_unsigned = {k: v for k, v in request.agent_card.items() if k != 'signature'}

    is_valid = identity.verify_agent_card(agent_card_unsigned, request.signature, request.did)

    if is_valid:
        return VerifyAgentCardResponse(
            valid=True,
            message="Signature is valid. AgentCard is authentic and unmodified."
        )
    else:
        return VerifyAgentCardResponse(
            valid=False,
            message="Signature verification failed. Either the signature is invalid or the AgentCard has been tampered with."
        )
