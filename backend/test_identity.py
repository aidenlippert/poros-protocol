"""
Test script for identity module - DID generation and signature verification
"""

from app.identity import generate_keypair, sign_agent_card, verify_agent_card

# Test 1: Generate a keypair
print("=" * 60)
print("TEST 1: Generate Ed25519 Keypair and DID")
print("=" * 60)

did, private_key_pem = generate_keypair()
print(f"[OK] Generated DID: {did}")
print(f"[OK] Private key (PEM): {private_key_pem[:50]}...")
print()

# Test 2: Sign an AgentCard
print("=" * 60)
print("TEST 2: Sign AgentCard")
print("=" * 60)

agent_card = {
    "version": "2.0",
    "did": did,
    "agent_id": "test/demo-agent",
    "name": "Demo Agent",
    "description": "Testing cryptographic signatures",
    "endpoint": "https://example.com/agent",
    "capabilities": ["test", "demo"],
    "pricing": {"model": "free", "amount": 0},
    "metadata": {"category": "testing"}
}

signature = sign_agent_card(agent_card, private_key_pem)
print(f"✓ Signature: {signature}")
print()

# Test 3: Verify the signature
print("=" * 60)
print("TEST 3: Verify AgentCard Signature")
print("=" * 60)

is_valid = verify_agent_card(agent_card, signature, did)
print(f"✓ Signature valid: {is_valid}")
print()

# Test 4: Try to verify with wrong DID (should fail)
print("=" * 60)
print("TEST 4: Verify with Wrong DID (should fail)")
print("=" * 60)

wrong_did, _ = generate_keypair()
is_valid_wrong = verify_agent_card(agent_card, signature, wrong_did)
print(f"✓ Signature valid with wrong DID: {is_valid_wrong}")
print()

# Test 5: Try to verify tampered data (should fail)
print("=" * 60)
print("TEST 5: Verify Tampered Data (should fail)")
print("=" * 60)

tampered_card = agent_card.copy()
tampered_card["name"] = "Hacked Agent"
is_valid_tampered = verify_agent_card(tampered_card, signature, did)
print(f"✓ Signature valid for tampered data: {is_valid_tampered}")
print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"✓ Keypair generation: PASS")
print(f"✓ AgentCard signing: PASS")
print(f"✓ Valid signature verification: {'PASS' if is_valid else 'FAIL'}")
print(f"✓ Wrong DID rejection: {'PASS' if not is_valid_wrong else 'FAIL'}")
print(f"✓ Tampered data rejection: {'PASS' if not is_valid_tampered else 'FAIL'}")
print()

if is_valid and not is_valid_wrong and not is_valid_tampered:
    print("🎉 ALL TESTS PASSED! Identity module is working correctly.")
else:
    print("❌ SOME TESTS FAILED!")
