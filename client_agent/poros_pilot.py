"""
POROS PILOT v2.0
The Ultimate Personal AI Assistant

Features:
- LLM-powered intelligent task planning (Gemini)
- Multi-step workflow orchestration
- Confidence-based approval gates
- Poros Protocol integration
- Full autonomy when safe
"""

import httpx
import json
import os
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# Import our LLM planner
from llm_planner import LLMTaskPlanner, Task


class ApprovalMode(Enum):
    """How much human involvement is needed"""
    AUTO = "auto"  # 90%+ confidence
    NOTIFY = "notify"  # 70-90%
    CONFIRM = "confirm"  # 50-70%
    INTERACTIVE = "interactive"  # <50%


@dataclass
class Plan:
    """A multi-step execution plan"""
    id: str
    user_request: str
    tasks: List[Task]
    confidence: float
    approval_mode: ApprovalMode
    reasoning: str
    created_at: datetime
    status: str = "pending"


class PorosClient:
    """Client for Poros Protocol"""

    def __init__(self, backend_url: str = "https://poros-protocol-production.up.railway.app"):
        self.backend_url = backend_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def discover_agents(self, capability: str) -> List[Dict]:
        """Find agents by capability"""
        try:
            response = await self.client.post(
                f"{self.backend_url}/api/orchestrate/discover",
                json={"capability": capability}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("agents", [])
        except Exception as e:
            print(f"❌ Discovery failed: {e}")
            return []

    async def query_agent(self, agent_did: str, query: Dict) -> Dict:
        """Query a specific agent"""
        try:
            response = await self.client.post(
                f"{self.backend_url}/api/orchestrate/query",
                json={
                    "agent_did": agent_did,
                    "query": query
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return {"error": str(e)}


class PorosPilot:
    """The Poros Pilot - Your LLM-powered personal assistant"""

    def __init__(self, gemini_api_key: str = None):
        try:
            self.planner = LLMTaskPlanner(api_key=gemini_api_key)
            self.llm_enabled = True
            print("✅ LLM Planning: ENABLED (Gemini)")
        except Exception as e:
            print(f"⚠️  LLM Planning: DISABLED ({e})")
            print("   Using fallback pattern matching")
            self.llm_enabled = False
            self.planner = None

        self.poros = PorosClient()
        self.execution_history = []

    async def process_request(self, user_request: str) -> Dict:
        """Main entry point"""
        print(f"\n{'='*60}")
        print(f"📨 Request: {user_request}")
        print(f"{'='*60}\n")

        # Step 1: Create plan using LLM
        if self.llm_enabled:
            plan_data = self.planner.create_plan(user_request)
            plan = Plan(
                id=f"plan_{datetime.now().timestamp()}",
                user_request=user_request,
                tasks=plan_data["tasks"],
                confidence=plan_data["confidence"],
                approval_mode=self._calculate_approval_mode(plan_data["confidence"]),
                reasoning=plan_data["reasoning"],
                created_at=datetime.now()
            )
        else:
            # Fallback to simple patterns
            plan = self._fallback_plan(user_request)

        # Show plan details
        print(f"🧠 AI Reasoning: {plan.reasoning}")
        print(f"🎯 Confidence: {plan.confidence}%")
        print(f"🚦 Approval Mode: {plan.approval_mode.value}\n")

        # Step 2: Handle based on approval mode
        if plan.approval_mode == ApprovalMode.AUTO:
            print("✅ High confidence - executing automatically...\n")
            return await self._execute_plan(plan)

        elif plan.approval_mode == ApprovalMode.NOTIFY:
            print("📢 Executing with notification...\n")
            result = await self._execute_plan(plan)
            self._notify_user(plan, result)
            return result

        elif plan.approval_mode == ApprovalMode.CONFIRM:
            print("⏸️  Requesting your approval...\n")
            self._show_plan(plan)
            if self._request_approval():
                return await self._execute_plan(plan)
            else:
                return {"status": "cancelled", "message": "User declined"}

        else:  # INTERACTIVE
            print("❓ Need more information...\n")
            return self._interactive_mode(plan)

    def _calculate_approval_mode(self, confidence: float) -> ApprovalMode:
        """Determine approval mode from confidence"""
        if confidence >= 90:
            return ApprovalMode.AUTO
        elif confidence >= 70:
            return ApprovalMode.NOTIFY
        elif confidence >= 50:
            return ApprovalMode.CONFIRM
        else:
            return ApprovalMode.INTERACTIVE

    def _fallback_plan(self, user_request: str) -> Plan:
        """Simple fallback if LLM unavailable"""
        # Weather check
        if any(w in user_request.lower() for w in ["weather", "temperature"]):
            return Plan(
                id=f"plan_{datetime.now().timestamp()}",
                user_request=user_request,
                tasks=[Task(
                    id="weather_1",
                    action="get_weather",
                    agent_capability="weather_forecast",
                    parameters={"city": "San Francisco"}
                )],
                confidence=85.0,
                approval_mode=ApprovalMode.AUTO,
                reasoning="Simple weather query",
                created_at=datetime.now()
            )

        # Default: unclear
        return Plan(
            id=f"plan_{datetime.now().timestamp()}",
            user_request=user_request,
            tasks=[Task(
                id="clarify_1",
                action="clarify",
                parameters={"question": "Could you rephrase that?"}
            )],
            confidence=30.0,
            approval_mode=ApprovalMode.INTERACTIVE,
            reasoning="Could not understand request",
            created_at=datetime.now()
        )

    def _show_plan(self, plan: Plan):
        """Display plan to user"""
        print("📝 Execution Plan:")
        print("-" * 60)
        for i, task in enumerate(plan.tasks, 1):
            deps = f" (after: {', '.join(task.depends_on)})" if task.depends_on else ""
            print(f"  {i}. {task.action}{deps}")
            if task.agent_capability:
                print(f"     Agent: {task.agent_capability}")
            if task.parameters:
                print(f"     Params: {task.parameters}")
            if hasattr(task, 'reasoning') and task.reasoning:
                print(f"     Why: {task.reasoning}")
        print("-" * 60)

    def _request_approval(self) -> bool:
        """Ask for approval"""
        while True:
            response = input("\n✅ Approve? [Y/n]: ").strip().lower()
            if response in ['y', 'yes', '']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please enter Y or N")

    async def _execute_plan(self, plan: Plan) -> Dict:
        """Execute the plan"""
        print("🚀 Executing...\n")
        results = []

        for i, task in enumerate(plan.tasks, 1):
            print(f"[{i}/{len(plan.tasks)}] {task.action}...")
            result = await self._execute_task(task)
            results.append(result)

            if "error" in result:
                print(f"   ❌ Failed: {result['error']}\n")
                task.status = "failed"
                break
            else:
                print(f"   ✓ Done\n")
                task.status = "completed"

        plan.status = "completed"
        self.execution_history.append(plan)

        return {
            "status": "success",
            "results": results
        }

    async def _execute_task(self, task: Task) -> Dict:
        """Execute a single task"""
        # Weather
        if task.action == "get_weather" or task.agent_capability == "weather_forecast":
            agents = await self.poros.discover_agents("weather_forecast")
            if not agents:
                return {"error": "No weather agent found"}

            agent = agents[0]
            city = task.parameters.get("city", "San Francisco")

            result = await self.poros.query_agent(
                agent["did"],
                {"action": "get_weather", "parameters": {"city": city}}
            )

            # Extract weather data
            if "response" in result:
                weather_data = result["response"].get("result", {})
                return {
                    "city": weather_data.get("location", city),
                    "temperature": weather_data.get("temperature"),
                    "condition": weather_data.get("condition")
                }

            return result

        # Calendar
        elif "calendar" in task.action:
            return {
                "slots": ["Mon 9am", "Tue 2pm", "Wed 10am"],
                "note": "Simulated - would call real calendar API"
            }

        # Discovery
        elif task.action == "find_agent" and task.agent_capability:
            agents = await self.poros.discover_agents(task.agent_capability)
            return {"found": len(agents), "agents": [a["name"] for a in agents]}

        # Clarification
        elif task.action == "clarify":
            return {"question": task.parameters.get("question")}

        # Generic
        else:
            return {"status": "simulated", "action": task.action}

    def _notify_user(self, plan: Plan, result: Dict):
        """Post-execution notification"""
        print("\n" + "="*60)
        print("📬 TASK COMPLETED")
        print("="*60)
        print(f"Request: {plan.user_request}")
        print(f"Status: {result.get('status')}")
        print(f"Time: {datetime.now().strftime('%I:%M %p')}")
        print("="*60 + "\n")

    def _interactive_mode(self, plan: Plan) -> Dict:
        """Interactive mode for unclear requests"""
        print("💬 I need more info:\n")
        for task in plan.tasks:
            if task.action == "clarify" and task.parameters:
                print(f"❓ {task.parameters.get('question')}")

        return {"status": "needs_clarification"}


# CLI
async def main():
    """Run Poros Pilot in CLI"""
    # Get Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n⚠️  Warning: GEMINI_API_KEY not set")
        print("   Set it with: export GEMINI_API_KEY=your_key")
        print("   Running in fallback mode...\n")

    pilot = PorosPilot(gemini_api_key=api_key)

    print("""
==============================================================
         POROS PILOT v2.0
         Powered by Gemini AI

  Your intelligent personal assistant
==============================================================
    """)

    print("💡 Try:")
    print("   'What's the weather in Tokyo?'")
    print("   'Book me a dentist appointment next Tuesday'")
    print("   'Plan a trip to Seattle'")
    print("   'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye!")
                break

            result = await pilot.process_request(user_input)

            if result.get("status") == "success":
                print("\n✅ Completed!\n")
                # Show results
                for r in result.get("results", []):
                    if "city" in r:
                        print(f"   {r['city']}: {r['temperature']}°F, {r['condition']}")
                    elif "slots" in r:
                        print(f"   Available: {', '.join(r['slots'])}")

            print("\n" + "-"*60 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
