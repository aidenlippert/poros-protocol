# Poros Protocol v2 Specification

**Version:** 2.0.0
**Status:** Draft
**Last Updated:** 2025-10-22

## Overview

The Poros Protocol is a lightweight, negotiation-first communication protocol for autonomous AI agents. Unlike task-delegation protocols (A2A) or master-slave protocols (MCP), Poros enables **peer-to-peer negotiation** and **multi-turn collaboration** between agents.

## Core Principles

1. **Negotiation-First:** Agents can propose, counter-propose, and commit to agreements
2. **Decentralized Identity:** Every agent has a cryptographic DID
3. **Verifiable Trust:** All actions are signed and attestable
4. **Simple Transport:** JSON over HTTPS (no complex SDKs required)
5. **Economic Layer:** Built-in support for paid agents and transactions

---

## AgentCard v2 Schema

Every agent publishes a signed AgentCard describing its capabilities.

```json
{
  "version": "2.0",
  "did": "did:poros:ed25519:Abc123XyZ...",
  "agent_id": "owner/agent-name",
  "name": "Dentist Scheduler Pro",
  "description": "Books dental appointments in the SF Bay Area",
  "endpoint": "https://dentist-agent.example.com",
  "capabilities": [
    {
      "name": "appointment_scheduling",
      "verbs": ["query", "propose", "commit"],
      "input_schema": {
        "location": "string",
        "specialty": "string",
        "date_range": "object"
      },
      "output_schema": {
        "available_slots": "array"
      }
    }
  ],
  "pricing": {
    "model": "per_transaction",
    "amount": 0.50,
    "currency": "USD"
  },
  "metadata": {
    "location": "San Francisco, CA",
    "languages": ["en"],
    "certifications": ["HIPAA compliant"]
  },
  "created_at": "2025-10-22T00:00:00Z",
  "signature": "base64_encoded_ed25519_signature"
}
```

### Required Fields
- `version`: Protocol version (string)
- `did`: Decentralized Identifier (string)
- `agent_id`: Human-readable ID (string, format: `owner/name`)
- `name`: Display name (string)
- `description`: What the agent does (string)
- `endpoint`: HTTPS URL for agent communication (string)
- `capabilities`: Array of capabilities (array)
- `signature`: Cryptographic signature of the card (string)

### Optional Fields
- `pricing`: Payment model (object)
- `metadata`: Additional info for discovery (object)

---

## Protocol Verbs

Poros defines 5 core verbs for agent interaction:

### 1. DISCOVER

**Purpose:** Find agents matching criteria
**Initiated by:** Client Agent or Orchestrator
**Endpoint:** `POST /orchestrate/discover`

**Request:**
```json
{
  "capability": "appointment_scheduling",
  "filters": {
    "location": "San Francisco",
    "max_price": 1.00
  }
}
```

**Response:**
```json
{
  "agents": [
    {
      "did": "did:poros:ed25519:Abc123...",
      "agent_id": "medcal/dentist-scheduler",
      "name": "MedCal Dentist Scheduler",
      "reputation_score": 0.95,
      "pricing": {"amount": 0.50}
    }
  ]
}
```

### 2. QUERY

**Purpose:** Ask an agent a question or request information
**Initiated by:** Client Agent
**Endpoint:** `POST /orchestrate/query`

**Request:**
```json
{
  "agent_did": "did:poros:ed25519:Abc123...",
  "query": {
    "action": "check_availability",
    "parameters": {
      "specialty": "general_dentistry",
      "date_range": {
        "start": "2025-10-25",
        "end": "2025-10-31"
      }
    }
  }
}
```

**Response:**
```json
{
  "agent_did": "did:poros:ed25519:Abc123...",
  "response": {
    "available_slots": [
      {
        "datetime": "2025-10-27T14:00:00Z",
        "duration_minutes": 60,
        "provider": "Dr. Smith",
        "price": 150.00
      }
    ]
  },
  "signature": "..."
}
```

### 3. PROPOSE

**Purpose:** Make a formal proposal for a transaction
**Initiated by:** Client Agent
**Endpoint:** `POST /orchestrate/propose`

**Request:**
```json
{
  "agent_did": "did:poros:ed25519:Abc123...",
  "proposal": {
    "action": "book_appointment",
    "parameters": {
      "slot": "2025-10-27T14:00:00Z",
      "patient": {
        "name": "John Doe",
        "email": "john@example.com"
      }
    },
    "max_price": 150.00
  }
}
```

**Response:**
```json
{
  "proposal_id": "prop_xyz789",
  "status": "accepted",
  "reservation": {
    "slot": "2025-10-27T14:00:00Z",
    "provider": "Dr. Smith",
    "expires_at": "2025-10-22T12:00:00Z"
  },
  "signature": "..."
}
```

### 4. COMMIT

**Purpose:** Finalize an accepted proposal
**Initiated by:** Client Agent
**Endpoint:** `POST /orchestrate/commit`

**Request:**
```json
{
  "agent_did": "did:poros:ed25519:Abc123...",
  "proposal_id": "prop_xyz789",
  "payment_proof": "stripe_payment_intent_abc123"
}
```

**Response:**
```json
{
  "commitment_id": "commit_abc123",
  "status": "confirmed",
  "confirmation": {
    "appointment_id": "appt_456",
    "confirmation_code": "CONF-789",
    "details": {...}
  },
  "signature": "..."
}
```

### 5. CANCEL

**Purpose:** Cancel a committed transaction
**Initiated by:** Client Agent or Specialist Agent
**Endpoint:** `POST /orchestrate/cancel`

**Request:**
```json
{
  "commitment_id": "commit_abc123",
  "reason": "Patient requested cancellation",
  "refund_requested": true
}
```

**Response:**
```json
{
  "status": "cancelled",
  "refund_issued": true,
  "signature": "..."
}
```

---

## Identity & Signatures

### DID Format

Poros uses `did:poros:<method>:<identifier>` format:
- Example: `did:poros:ed25519:Abc123XyZ...`

### Signing AgentCards

1. Canonicalize the AgentCard JSON (deterministic key ordering)
2. Hash with SHA-256
3. Sign with Ed25519 private key
4. Base64-encode signature
5. Add `signature` field to AgentCard

### Verification

1. Extract signature from AgentCard
2. Remove signature field from card
3. Canonicalize remaining JSON
4. Verify signature against DID's public key

---

## Reputation System (Proof-of-Reputation)

### Attestations

After each interaction, both parties sign an attestation:

```json
{
  "attestation_id": "att_xyz",
  "agent_did": "did:poros:ed25519:Abc123...",
  "attester_did": "did:poros:ed25519:Def456...",
  "interaction_id": "commit_abc123",
  "metrics": {
    "success": true,
    "latency_ms": 350,
    "quality_score": 4.5
  },
  "timestamp": "2025-10-22T10:00:00Z",
  "signature": "..."
}
```

### Reputation Score Calculation

```python
def calculate_reputation(agent_did):
    attestations = get_attestations(agent_did)

    # Weighted by attester reputation
    weighted_score = sum(
        att.quality_score * attester_reputation(att.attester_did)
        for att in attestations
    )

    total_weight = sum(attester_reputation(att.attester_did) for att in attestations)

    return weighted_score / total_weight if total_weight > 0 else 0.5
```

---

## Economic Model

### Payment Flow

1. **Discovery:** Client finds agent with pricing info
2. **Quote:** Agent provides quote in PROPOSE response
3. **Escrow:** Client deposits funds with Orchestrator
4. **Commit:** Transaction confirmed
5. **Release:** Orchestrator releases payment to agent (minus fee)

### Pricing Models

- `free`: No charge
- `per_transaction`: Fixed fee per successful transaction
- `per_query`: Charge for each query
- `subscription`: Monthly/annual subscription
- `custom`: Agent-defined pricing logic

---

## Security Considerations

1. **Rate Limiting:** Orchestrator enforces rate limits per agent/user
2. **Signature Verification:** All AgentCards and responses must be signed
3. **HTTPS Only:** All communication over TLS
4. **API Keys:** Agents use API keys for authentication
5. **Sandboxing:** Agent code runs in isolated containers

---

## Reference Implementation

See:
- Backend: `/backend/app/orchestrator.py`
- Agent SDK: `/sdk/python/poros_sdk/`
- Example Agent: `/examples/dentist_agent.py`

---

## Changelog

### v2.0.0 (2025-10-22)
- Initial protocol specification
- Define 5 core verbs (DISCOVER, QUERY, PROPOSE, COMMIT, CANCEL)
- AgentCard v2 schema with DIDs and signatures
- Reputation system (Proof-of-Reputation)
- Economic layer with multiple pricing models
