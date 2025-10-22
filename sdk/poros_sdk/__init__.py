"""
Poros SDK - Build AI agents for the Poros Protocol

Simple Python SDK for registering and running agents on the Poros network.
"""

from .client import PorosClient
from .identity import generate_did, sign_agent_card

__version__ = "0.1.0"
__all__ = ["PorosClient", "generate_did", "sign_agent_card"]
