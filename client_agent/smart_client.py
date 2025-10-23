"""
POROS SMART CLIENT AGENT
The brain of your personal AI assistant.

Features:
- Multi-step task planning
- Confidence scoring (0-100%)
- Human approval gates
- Autonomous execution when safe
- Works with Poros Protocol agents
"""

import httpx
import json
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ApprovalMode(Enum):
    """How much human involvement is needed"""
    AUTO = "auto"  # 90%+ confidence - just do it
    NOTIFY = "notify"  # 70-90% - do it, then tell me
    CONFIRM = "confirm"  # 50-70% - show plan, wait for approval
    INTERACTIVE = "interactive"  # <50% - I need to help


@dataclass
class Task:
    """A single task step"""
    id: str
    action: str
    agent_capability: Optional[str] = None
    parameters: Dict[str, Any] = None
    depends_on: List[str] = None
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class Plan:
    """A multi-step execution plan"""
    id: str
    user_request: str
    tasks: List[Task]
    confidence: float
    approval_mode: ApprovalMode
    created_at: datetime
    status: str = "pending"


class TaskPlanner:
    """Breaks down high-level requests into executable steps"""

    def __init__(self):
        # Simple pattern matching for MVP
        # Later: Replace with LLM
        self.patterns = {
            "weather": {
                "keywords": ["weather", "temperature", "forecast", "rain", "sunny"],
                "tasks": [
                    Task(
                        id="weather_1",
                        action="get_weather",
                        agent_capability="weather_forecast",
                        parameters={"city": "extracted_city"}
                    )
                ],
                "confidence": 95.0
            },
            "book_dentist": {
                "keywords": ["dentist", "appointment", "book", "schedule"],
                "tasks": [
                    Task(id="check_cal", action="check_calendar"),
                    Task(id="find_dentist", action="find_agent",
                         agent_capability="dentist_search"),
                    Task(id="book", action="book_appointment",
                         depends_on=["check_cal", "find_dentist"])
                ],
                "confidence": 65.0  # Needs approval
            },
            "plan_trip": {
                "keywords": ["trip", "travel", "vacation", "visit"],
                "tasks": [
                    Task(id="research", action="research_destination"),
                    Task(id="flights", action="search_flights"),
                    Task(id="hotel", action="search_hotels"),
                    Task(id="budget", action="calculate_budget",
                         depends_on=["flights", "hotel"])
                ],
                "confidence": 60.0  # Needs approval
            }
        }

    def create_plan(self, user_request: str) -> Plan:
        """Create an execution plan from user request"""
        # Simple pattern matching
        request_lower = user_request.lower()

        for pattern_name, pattern_data in self.patterns.items():
            if any(keyword in request_lower for keyword in pattern_data["keywords"]):
                return Plan(
                    id=f"plan_{datetime.now().timestamp()}",
                    user_request=user_request,
                    tasks=pattern_data["tasks"],
                    confidence=pattern_data["confidence"],
                    approval_mode=self._calculate_approval_mode(pattern_data["confidence"]),
                    created_at=datetime.now()
                )

        # Unknown task
        return Plan(
            id=f"plan_{datetime.now().timestamp()}",
            user_request=user_request,
            tasks=[Task(id="unknown", action="clarify",
                       parameters={"question": "What would you like me to do?"})],
            confidence=30.0,
            approval_mode=ApprovalMode.INTERACTIVE,
            created_at=datetime.now()
        )

    def _calculate_approval_mode(self, confidence: float) -> ApprovalMode:
        """Determine how much human involvement needed"""
        if confidence >= 90:
            return ApprovalMode.AUTO
        elif confidence >= 70:
            return ApprovalMode.NOTIFY
        elif confidence >= 50:
            return ApprovalMode.CONFIRM
        else:
            return ApprovalMode.INTERACTIVE


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


class SmartClientAgent:
    """The Smart Client Agent - Your Personal AI Assistant"""

    def __init__(self):
        self.planner = TaskPlanner()
        self.poros = PorosClient()
        self.execution_history = []

    async def process_request(self, user_request: str) -> Dict:
        """Main entry point - process a user request"""
        print(f"\n{'='*60}")
        print(f"📨 User Request: {user_request}")
        print(f"{'='*60}\n")

        # Step 1: Create plan
        plan = self.planner.create_plan(user_request)
        print(f"📋 Plan created: {len(plan.tasks)} tasks")
        print(f"🎯 Confidence: {plan.confidence}%")
        print(f"🚦 Approval Mode: {plan.approval_mode.value}\n")

        # Step 2: Handle based on approval mode
        if plan.approval_mode == ApprovalMode.AUTO:
            print("✅ High confidence - executing automatically...\n")
            return await self._execute_plan(plan)

        elif plan.approval_mode == ApprovalMode.NOTIFY:
            print("📢 Will execute and notify you...\n")
            result = await self._execute_plan(plan)
            self._notify_user(plan, result)
            return result

        elif plan.approval_mode == ApprovalMode.CONFIRM:
            print("⏸️  Waiting for your approval...\n")
            self._show_plan(plan)
            if self._request_approval():
                return await self._execute_plan(plan)
            else:
                return {"status": "cancelled", "message": "User cancelled"}

        else:  # INTERACTIVE
            print("❓ I need more information...\n")
            return self._interactive_mode(plan)

    def _show_plan(self, plan: Plan):
        """Display the plan to user"""
        print("📝 Execution Plan:")
        print("-" * 60)
        for i, task in enumerate(plan.tasks, 1):
            deps = f" (depends on: {', '.join(task.depends_on)})" if task.depends_on else ""
            print(f"  {i}. {task.action}{deps}")
            if task.parameters:
                print(f"     Parameters: {task.parameters}")
        print("-" * 60)

    def _request_approval(self) -> bool:
        """Ask user for approval"""
        while True:
            response = input("\n✅ Approve and execute? [Y/n]: ").strip().lower()
            if response in ['y', 'yes', '']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter Y or N")

    async def _execute_plan(self, plan: Plan) -> Dict:
        """Execute all tasks in the plan"""
        print("🚀 Executing plan...\n")
        results = []

        for task in plan.tasks:
            print(f"▶️  Executing: {task.action}")
            result = await self._execute_task(task, plan)
            task.result = result
            task.status = "completed" if "error" not in result else "failed"
            results.append(result)
            print(f"   ✓ Done\n")

        plan.status = "completed"
        self.execution_history.append(plan)

        return {
            "status": "success",
            "plan_id": plan.id,
            "results": results
        }

    async def _execute_task(self, task: Task, plan: Plan) -> Dict:
        """Execute a single task"""
        # Handle different task types
        if task.action == "get_weather":
            # Discover weather agent
            agents = await self.poros.discover_agents("weather_forecast")
            if not agents:
                return {"error": "No weather agent found"}

            # Query the agent
            agent = agents[0]
            result = await self.poros.query_agent(
                agent["did"],
                {
                    "action": "get_weather",
                    "parameters": task.parameters or {"city": "San Francisco"}
                }
            )
            return result

        elif task.action == "check_calendar":
            # Simulated for MVP
            return {
                "available_slots": [
                    "Monday 9am-12pm",
                    "Tuesday 2pm-5pm",
                    "Wednesday 10am-3pm"
                ]
            }

        elif task.action == "find_agent":
            agents = await self.poros.discover_agents(task.agent_capability)
            return {"agents_found": len(agents), "agents": agents}

        elif task.action == "clarify":
            return {"question": task.parameters.get("question")}

        else:
            return {"status": "simulated", "action": task.action}

    def _notify_user(self, plan: Plan, result: Dict):
        """Notify user after execution"""
        print("\n" + "="*60)
        print("📬 NOTIFICATION: Task Completed")
        print("="*60)
        print(f"Request: {plan.user_request}")
        print(f"Status: {result.get('status')}")
        print(f"Completed at: {datetime.now().strftime('%I:%M %p')}")
        print("="*60 + "\n")

    def _interactive_mode(self, plan: Plan) -> Dict:
        """Interactive clarification mode"""
        print("💬 Interactive Mode - I need to ask you some questions:\n")
        for task in plan.tasks:
            if task.action == "clarify":
                print(f"❓ {task.parameters.get('question')}")

        return {
            "status": "needs_clarification",
            "plan_id": plan.id
        }


# CLI Interface
async def main():
    """Run the Smart Client Agent in CLI mode"""
    agent = SmartClientAgent()

    print("""
==============================================================
         POROS SMART CLIENT AGENT v1.0

  Your intelligent personal assistant
  Powered by Poros Protocol
==============================================================
    """)

    print("💡 Try these commands:")
    print("   - 'What's the weather in Tokyo?'")
    print("   - 'Book me a dentist appointment'")
    print("   - 'Plan a trip to Seattle'")
    print("   - 'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye!")
                break

            result = await agent.process_request(user_input)

            if result.get("status") == "success":
                print("\n✅ Task completed successfully!")
            elif result.get("status") == "cancelled":
                print("\n❌ Task cancelled")
            else:
                print(f"\n⚠️  Result: {json.dumps(result, indent=2)}")

            print("\n" + "-"*60 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
