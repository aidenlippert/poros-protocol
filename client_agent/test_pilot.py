"""
Quick test of Poros Pilot
Tests the "Book dentist" workflow
"""

import asyncio
import os
from poros_pilot import PorosPilot


async def test_dentist_booking():
    """Test the dentist booking workflow"""

    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n⚠️  GEMINI_API_KEY not found!")
        print("Please set it first:")
        print("  Windows: set GEMINI_API_KEY=your_key")
        print("  Linux/Mac: export GEMINI_API_KEY=your_key\n")
        return

    print("="*60)
    print("TESTING POROS PILOT - DENTIST BOOKING WORKFLOW")
    print("="*60)
    print()

    # Create the pilot
    pilot = PorosPilot(gemini_api_key=api_key)

    # Test requests
    test_cases = [
        "What's the weather in Tokyo?",
        "Book me a dentist appointment for next Tuesday"
    ]

    for request in test_cases:
        print(f"\n{'='*60}")
        print(f"TEST: {request}")
        print('='*60)

        try:
            result = await pilot.process_request(request)
            print(f"\nFinal Result: {result}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        input("\n\nPress Enter to continue to next test...")


if __name__ == "__main__":
    asyncio.run(test_dentist_booking())
