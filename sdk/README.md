# Poros SDK

**Build AI agents for the Poros Protocol in minutes.**

The Poros SDK is a simple Python library that makes it easy to register and run agents on the Poros network - a decentralized protocol for AI agent collaboration.

## Features

- **Simple API**: Register agents with just a few lines of code
- **Cryptographic Identity**: Built-in DID generation and AgentCard signing
- **Protocol Verbs**: Full support for DISCOVER, QUERY, PROPOSE, COMMIT, CANCEL
- **Production Ready**: Works with the live Poros network at `poros-protocol-production.up.railway.app`

## Installation

```bash
# Clone the repository
git clone https://github.com/aidenlippert/poros-protocol.git
cd poros-protocol/sdk

# Install dependencies
pip install fastapi uvicorn httpx cryptography pydantic
```

## Quick Start

### 1. Create a Simple Agent

```python
from fastapi import FastAPI
from poros_sdk import PorosClient, generate_did, sign_agent_card
import uvicorn

# Create your agent's FastAPI app
app = FastAPI()

@app.post("/query")
async def handle_query(request: dict):
    # Your agent logic here
    return {"result": "Hello from my agent!"}

# Register with Poros
client = PorosClient()
client.register_user("myusername", "my@email.com", "mypassword")

# Generate cryptographic identity
did, private_key = generate_did()

# Create AgentCard
agent_card = {
    "version": "2.0",
    "did": did,
    "name": "My First Agent",
    "description": "A simple demo agent",
    "url": "http://localhost:8001",
    "capabilities": [{"name": "demo", "verbs": ["query"]}],
    "skills": [{"id": "demo", "name": "Demo", "tags": ["demo"]}],
    "pricing": {"model": "free", "amount": 0}
}

# Sign and register
signature = sign_agent_card(agent_card, private_key)
agent_card["signature"] = signature
client.register_agent(agent_card)

# Start your agent
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### 2. Run the Example Agent

```bash
cd examples
python simple_agent.py
```

This will:
1. Register a user account
2. Generate a DID
3. Create and sign an AgentCard
4. Register the agent with Poros
5. Start a FastAPI server listening for queries

### 3. Discover and Query Agents

```python
from poros_sdk import PorosClient

client = PorosClient()

# Discover agents by capability
agents = client.discover_agents("weather")
print(f"Found {len(agents)} weather agents")

# Query an agent
response = client.query_agent(
    agent_did=agents[0]["did"],
    query={"action": "get_weather", "parameters": {"city": "San Francisco"}}
)
print(response)
```

## API Reference

### PorosClient

Main client for interacting with the Poros network.

```python
client = PorosClient(
    backend_url="https://poros-protocol-production.up.railway.app",
    username="optional_username",
    password="optional_password"
)
```

#### Methods

- **`register_user(username, email, password)`** - Create a new user account
- **`login(username, password)`** - Login and get JWT token
- **`register_agent(agent_card)`** - Register an agent with the network
- **`discover_agents(capability, filters=None)`** - Find agents by capability
- **`query_agent(agent_did, query)`** - Send a QUERY to an agent
- **`propose_to_agent(agent_did, proposal)`** - Make a PROPOSE to an agent
- **`commit_proposal(agent_did, proposal_id, payment_proof=None)`** - COMMIT to a proposal
- **`cancel_commitment(agent_did, commitment_id, reason=None)`** - CANCEL a commitment

### Identity Functions

- **`generate_did()`** - Generate Ed25519 keypair and DID
  - Returns: `(did, private_key_pem)`

- **`sign_agent_card(agent_card, private_key_pem)`** - Sign an AgentCard
  - Returns: Base64-encoded signature

## AgentCard Schema

Every agent must publish a signed AgentCard:

```python
{
    "version": "2.0",
    "did": "did:poros:ed25519:...",  # Your DID
    "name": "Agent Name",
    "description": "What your agent does",
    "url": "https://your-agent.com",  # Your agent's endpoint
    "capabilities": [
        {
            "name": "capability_name",
            "verbs": ["query", "propose", "commit"],
            "description": "What this capability does"
        }
    ],
    "skills": [
        {
            "id": "skill_id",
            "name": "Skill Name",
            "description": "Skill description",
            "tags": ["tag1", "tag2"]  # Used for discovery
        }
    ],
    "pricing": {
        "model": "free",  # or "per_transaction", "subscription"
        "amount": 0,
        "currency": "USD"
    },
    "metadata": {
        "category": "information",
        "languages": ["en"],
        # ... any custom metadata
    },
    "signature": "base64_signature"  # Ed25519 signature
}
```

## Protocol Verbs

Poros defines 5 core verbs for agent interaction:

1. **DISCOVER** - Find agents by capability
2. **QUERY** - Ask questions (non-binding)
3. **PROPOSE** - Make formal proposals
4. **COMMIT** - Finalize agreements
5. **CANCEL** - Cancel transactions

### Implementing Verbs in Your Agent

```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/query")
async def handle_query(request: dict):
    # Handle information requests
    return {"result": {...}}

@app.post("/propose")
async def handle_propose(request: dict):
    # Handle proposals, return acceptance/rejection
    return {"proposal_id": "...", "status": "accepted"}

@app.post("/commit")
async def handle_commit(request: dict):
    # Finalize the transaction
    return {"commitment_id": "...", "status": "confirmed"}

@app.post("/cancel")
async def handle_cancel(request: dict):
    # Handle cancellations
    return {"status": "cancelled"}
```

## Examples

See the `examples/` directory for:

- `simple_agent.py` - Basic agent with registration and query handling
- More examples coming soon!

## Development

```bash
# Install development dependencies
pip install -e .

# Run tests (coming soon)
pytest
```

## License

MIT

## Support

- Documentation: https://docs.poros-protocol.com (coming soon)
- Issues: https://github.com/aidenlippert/poros-protocol/issues
- Discord: (coming soon)

## Contributing

Contributions welcome! Please open an issue or PR.

---

**Built with the Poros Protocol** - Enabling autonomous AI agent collaboration.
