"""
Poros Protocol v2 - Verb Implementations

Implements the 5 core verbs: DISCOVER, QUERY, PROPOSE, COMMIT, CANCEL
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx

from .models import RegisteredAgent
from .database import get_session
from . import identity

router = APIRouter(prefix="/orchestrate", tags=["Poros Protocol v2"])


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class DiscoverRequest(BaseModel):
    capability: str
    filters: Optional[Dict[str, Any]] = None


class DiscoverResponse(BaseModel):
    agents: List[Dict[str, Any]]


class QueryRequest(BaseModel):
    agent_did: str
    query: Dict[str, Any]


class QueryResponse(BaseModel):
    agent_did: str
    response: Dict[str, Any]
    signature: Optional[str] = None


class ProposeRequest(BaseModel):
    agent_did: str
    proposal: Dict[str, Any]


class ProposeResponse(BaseModel):
    proposal_id: str
    status: str
    reservation: Optional[Dict[str, Any]] = None
    signature: Optional[str] = None


class CommitRequest(BaseModel):
    agent_did: str
    proposal_id: str
    payment_proof: Optional[str] = None


class CommitResponse(BaseModel):
    commitment_id: str
    status: str
    confirmation: Optional[Dict[str, Any]] = None
    signature: Optional[str] = None


class CancelRequest(BaseModel):
    agent_did: str
    commitment_id: str
    reason: Optional[str] = None
    refund_requested: bool = False


class CancelResponse(BaseModel):
    status: str
    refund_issued: bool = False
    signature: Optional[str] = None


# ============================================
# VERB ENDPOINTS
# ============================================

@router.post("/discover", response_model=DiscoverResponse)
async def discover_agents(
    request: DiscoverRequest,
    session: Session = Depends(get_session)
):
    """
    DISCOVER verb - Find agents matching capability criteria.

    This endpoint searches the registry for agents that have the requested
    capability and match optional filters like location, price, etc.
    """
    # Query agents by capability (stored in skills_tags)
    statement = select(RegisteredAgent).where(
        RegisteredAgent.is_active == True
    )
    all_agents = session.exec(statement).all()

    # Filter by capability
    matching_agents = []
    for agent in all_agents:
        # Check if capability matches:
        # 1. In skills_tags (flattened tags)
        # 2. In capabilities[].name (capability name)
        # 3. In skills[].id (skill ID)
        matched = False

        if request.capability in agent.skills_tags:
            matched = True

        # Check agent_card capabilities
        capabilities = agent.agent_card.get("capabilities", [])
        for cap in capabilities:
            if cap.get("name") == request.capability:
                matched = True
                break

        # Check agent_card skills
        skills = agent.agent_card.get("skills", [])
        for skill in skills:
            if skill.get("id") == request.capability:
                matched = True
                break

        if matched:
            matching_agents.append(agent)

    # Apply additional filters
    if request.filters:
        filtered = []
        for agent in matching_agents:
            # Filter by max_price
            if "max_price" in request.filters:
                pricing = agent.agent_card.get("pricing", {})
                agent_price = pricing.get("amount", 0)
                if agent_price > request.filters["max_price"]:
                    continue

            # Filter by location (if in metadata)
            if "location" in request.filters:
                metadata = agent.agent_card.get("metadata", {})
                agent_location = metadata.get("location", "")
                if request.filters["location"].lower() not in agent_location.lower():
                    continue

            filtered.append(agent)
        matching_agents = filtered

    # Build response
    agents_response = []
    for agent in matching_agents:
        agents_response.append({
            "did": agent.did or f"did:poros:legacy:{agent.agent_id}",
            "agent_id": agent.agent_id,
            "name": agent.name,
            "reputation_score": agent.success_rate,  # Use success_rate as reputation for now
            "pricing": agent.agent_card.get("pricing", {"model": "free", "amount": 0})
        })

    return DiscoverResponse(agents=agents_response)


@router.post("/query", response_model=QueryResponse)
async def query_agent(
    request: QueryRequest,
    session: Session = Depends(get_session)
):
    """
    QUERY verb - Ask an agent a question or request information.

    This is a lightweight, non-binding request for information.
    No commitments are made in a QUERY.
    """
    # Find the agent by DID
    statement = select(RegisteredAgent).where(RegisteredAgent.did == request.agent_did)
    agent = session.exec(statement).first()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with DID {request.agent_did} not found")

    if not agent.is_active:
        raise HTTPException(status_code=400, detail="Agent is not active")

    # Forward query to agent's endpoint
    agent_url = agent.url
    if not agent_url.endswith("/query"):
        agent_url = f"{agent_url}/query"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(agent_url, json=request.query)
            response.raise_for_status()
            agent_response = response.json()

        return QueryResponse(
            agent_did=request.agent_did,
            response=agent_response,
            signature=agent_response.get("signature")
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to communicate with agent: {str(e)}"
        )


@router.post("/propose", response_model=ProposeResponse)
async def propose_to_agent(
    request: ProposeRequest,
    session: Session = Depends(get_session)
):
    """
    PROPOSE verb - Make a formal proposal for a transaction.

    The agent can accept, reject, or counter-propose.
    """
    # Find the agent
    statement = select(RegisteredAgent).where(RegisteredAgent.did == request.agent_did)
    agent = session.exec(statement).first()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with DID {request.agent_did} not found")

    # Forward proposal to agent's endpoint
    agent_url = agent.url
    if not agent_url.endswith("/propose"):
        agent_url = f"{agent_url}/propose"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(agent_url, json=request.proposal)
            response.raise_for_status()
            agent_response = response.json()

        return ProposeResponse(
            proposal_id=agent_response.get("proposal_id"),
            status=agent_response.get("status"),
            reservation=agent_response.get("reservation"),
            signature=agent_response.get("signature")
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to communicate with agent: {str(e)}"
        )


@router.post("/commit", response_model=CommitResponse)
async def commit_proposal(
    request: CommitRequest,
    session: Session = Depends(get_session)
):
    """
    COMMIT verb - Finalize an accepted proposal.

    This confirms the transaction and may include payment proof.
    """
    # Find the agent
    statement = select(RegisteredAgent).where(RegisteredAgent.did == request.agent_did)
    agent = session.exec(statement).first()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with DID {request.agent_did} not found")

    # Forward commit to agent's endpoint
    agent_url = agent.url
    if not agent_url.endswith("/commit"):
        agent_url = f"{agent_url}/commit"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                agent_url,
                json={
                    "proposal_id": request.proposal_id,
                    "payment_proof": request.payment_proof
                }
            )
            response.raise_for_status()
            agent_response = response.json()

        return CommitResponse(
            commitment_id=agent_response.get("commitment_id"),
            status=agent_response.get("status"),
            confirmation=agent_response.get("confirmation"),
            signature=agent_response.get("signature")
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to communicate with agent: {str(e)}"
        )


@router.post("/cancel", response_model=CancelResponse)
async def cancel_commitment(
    request: CancelRequest,
    session: Session = Depends(get_session)
):
    """
    CANCEL verb - Cancel a committed transaction.

    Can be initiated by either the client or the agent.
    May include refund processing.
    """
    # Find the agent
    statement = select(RegisteredAgent).where(RegisteredAgent.did == request.agent_did)
    agent = session.exec(statement).first()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with DID {request.agent_did} not found")

    # Forward cancellation to agent's endpoint
    agent_url = agent.url
    if not agent_url.endswith("/cancel"):
        agent_url = f"{agent_url}/cancel"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                agent_url,
                json={
                    "commitment_id": request.commitment_id,
                    "reason": request.reason,
                    "refund_requested": request.refund_requested
                }
            )
            response.raise_for_status()
            agent_response = response.json()

        return CancelResponse(
            status=agent_response.get("status"),
            refund_issued=agent_response.get("refund_issued", False),
            signature=agent_response.get("signature")
        )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to communicate with agent: {str(e)}"
        )
