"""
Test end-to-end QUERY flow after DID fix
"""
import sys
sys.path.insert(0, 'sdk')

from poros_sdk import PorosClient, generate_did, sign_agent_card
import json

print("=" * 60)
print("TESTING END-TO-END QUERY FLOW")
print("=" * 60)

# Step 1: Register user and get token
print("\n[1/4] Registering user...")
client = PorosClient(backend_url="https://poros-protocol-production.up.railway.app")

# Use a unique username with timestamp
import time
username = f'weather_test_{int(time.time())}'

try:
    token = client.register_user(username, f'{username}@poros.com', 'pass123')
    print(f"[OK] User registered: {username}")
    print(f"[OK] Token: {token[:20]}...")
except Exception as e:
    print(f"[ERROR] Registration failed: {e}")
    sys.exit(1)

# Step 2: Generate DID and register agent
print("\n[2/4] Generating DID and registering agent...")
did, private_key = generate_did()
print(f"[OK] Generated DID: {did}")

agent_card = {
    "version": "2.0",
    "did": did,
    "name": "Poros Weather Service (Test)",
    "description": "Real-time weather information for any city",
    "url": "https://positive-expression-production-8aa0.up.railway.app",
    "capabilities": ["weather_forecast"],
    "skills": ["weather_data", "forecasting"],  # Added required field
    "pricing": {
        "model": "free",
        "price_per_query": 0
    },
    "actions": [
        {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "city": {"type": "string", "required": True},
                "country_code": {"type": "string", "required": False}
            }
        }
    ]
}

# Sign the agent card
signature = sign_agent_card(agent_card, private_key)
agent_card["signature"] = signature

# Register
try:
    result = client.register_agent(agent_card)
    print(f"[OK] Agent registered!")
    print(f"  Agent ID: {result.get('agent_id')}")
    print(f"  DID in response: {result.get('did')}")
except Exception as e:
    print(f"[ERROR] Agent registration failed: {e}")
    # Try to get detailed error from response
    import httpx
    try:
        response = httpx.post(
            "https://poros-protocol-production.up.railway.app/api/registry/agents",
            headers={"Authorization": f"Bearer {client._token}"},
            json={"agent_card": agent_card}
        )
        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Response: {response.text}")
    except:
        pass
    sys.exit(1)

result = result or {}

if not result.get('did'):
    print("\n[ERROR] CRITICAL: DID is still NULL in database!")
    print("The fix did not work. Stopping test.")
    sys.exit(1)

# Step 3: Discover the agent
print("\n[3/4] Testing DISCOVER endpoint...")
agents = client.discover_agents("weather_forecast")
print(f"[OK] Found {len(agents)} weather agents")

# Find our agent
our_agent = None
for agent in agents:
    if agent.get('did') == did:
        our_agent = agent
        break

if our_agent:
    print(f"[OK] Found our agent in discovery!")
    print(f"  DID: {our_agent['did']}")
    print(f"  Name: {our_agent['name']}")
else:
    print("[INFO] Our agent not found in discovery yet (may need a moment)")

# Step 4: Test end-to-end QUERY
print("\n[4/4] Testing end-to-end QUERY through orchestrator...")
try:
    response = client.query_agent(did, {
        "action": "get_weather",
        "parameters": {"city": "Tokyo"}
    })
    print("[OK] QUERY SUCCESSFUL!")
    print(f"\nResponse:")
    print(json.dumps(response, indent=2))

    # The response is nested: response.response.result
    agent_response = response.get('response', {})
    if agent_response.get('status') == 'success':
        result = agent_response.get('result', {})
        print(f"\n[SUCCESS] END-TO-END TEST PASSED!")
        print(f"   Agent DID: {response.get('agent_did')}")
        print(f"   Location: {result.get('location')}")
        print(f"   Temperature: {result.get('temperature')} degrees F")
        print(f"   Condition: {result.get('condition')}")
        print(f"   Description: {result.get('description')}")
    else:
        print(f"\n[INFO] Query returned non-success status: {agent_response.get('status')}")

except Exception as e:
    print(f"[ERROR] QUERY FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
