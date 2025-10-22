"""
Poros Client - Communicate with the Poros Protocol backend
"""

import httpx
from typing import Dict, Any, Optional, List


class PorosClient:
    """Client for interacting with the Poros Protocol backend."""

    def __init__(
        self,
        backend_url: str = "https://poros-protocol-production.up.railway.app",
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize Poros client.

        Args:
            backend_url: URL of the Poros backend
            username: Your Poros username (optional)
            password: Your Poros password (optional)
        """
        self.backend_url = backend_url.rstrip('/')
        self.username = username
        self.password = password
        self._token: Optional[str] = None

    def register_user(self, username: str, email: str, password: str) -> str:
        """
        Register a new user account.

        Returns:
            JWT access token
        """
        response = httpx.post(
            f"{self.backend_url}/api/registry/users",
            json={"username": username, "email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self._token = data["access_token"]
        return self._token

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> str:
        """
        Login and get JWT token.

        Args:
            username: Username (uses self.username if not provided)
            password: Password (uses self.password if not provided)

        Returns:
            JWT access token
        """
        user = username or self.username
        pwd = password or self.password

        if not user or not pwd:
            raise ValueError("Username and password required")

        response = httpx.post(
            f"{self.backend_url}/api/registry/login",
            data={"username": user, "password": pwd}
        )
        response.raise_for_status()
        data = response.json()
        self._token = data["access_token"]
        return self._token

    def register_agent(self, agent_card: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register an agent with the Poros network.

        Args:
            agent_card: AgentCard dictionary

        Returns:
            Registered agent data
        """
        if not self._token:
            if self.username and self.password:
                self.login()
            else:
                raise ValueError("Not authenticated. Call login() first or provide username/password")

        response = httpx.post(
            f"{self.backend_url}/api/registry/agents",
            headers={"Authorization": f"Bearer {self._token}"},
            json={"agent_card": agent_card}
        )
        response.raise_for_status()
        return response.json()

    def discover_agents(self, capability: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Discover agents by capability.

        Args:
            capability: The capability to search for
            filters: Optional filters (e.g., max_price, location)

        Returns:
            List of matching agents
        """
        payload = {"capability": capability}
        if filters:
            payload["filters"] = filters

        response = httpx.post(
            f"{self.backend_url}/orchestrate/discover",
            json=payload
        )
        response.raise_for_status()
        return response.json()["agents"]

    def query_agent(self, agent_did: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a QUERY request to an agent.

        Args:
            agent_did: DID of the agent
            query: Query payload

        Returns:
            Agent's response
        """
        response = httpx.post(
            f"{self.backend_url}/orchestrate/query",
            json={"agent_did": agent_did, "query": query}
        )
        response.raise_for_status()
        return response.json()

    def propose_to_agent(self, agent_did: str, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a PROPOSE request to an agent.

        Args:
            agent_did: DID of the agent
            proposal: Proposal payload

        Returns:
            Agent's response (accepted/rejected/counter)
        """
        response = httpx.post(
            f"{self.backend_url}/orchestrate/propose",
            json={"agent_did": agent_did, "proposal": proposal}
        )
        response.raise_for_status()
        return response.json()

    def commit_proposal(self, agent_did: str, proposal_id: str, payment_proof: Optional[str] = None) -> Dict[str, Any]:
        """
        COMMIT to an accepted proposal.

        Args:
            agent_did: DID of the agent
            proposal_id: ID of the proposal to commit
            payment_proof: Optional payment proof

        Returns:
            Commitment confirmation
        """
        response = httpx.post(
            f"{self.backend_url}/orchestrate/commit",
            json={
                "agent_did": agent_did,
                "proposal_id": proposal_id,
                "payment_proof": payment_proof
            }
        )
        response.raise_for_status()
        return response.json()

    def cancel_commitment(
        self,
        agent_did: str,
        commitment_id: str,
        reason: Optional[str] = None,
        refund_requested: bool = False
    ) -> Dict[str, Any]:
        """
        CANCEL a committed transaction.

        Args:
            agent_did: DID of the agent
            commitment_id: ID of the commitment to cancel
            reason: Optional cancellation reason
            refund_requested: Whether to request a refund

        Returns:
            Cancellation confirmation
        """
        response = httpx.post(
            f"{self.backend_url}/orchestrate/cancel",
            json={
                "agent_did": agent_did,
                "commitment_id": commitment_id,
                "reason": reason,
                "refund_requested": refund_requested
            }
        )
        response.raise_for_status()
        return response.json()
