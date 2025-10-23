"""
LLM-Powered Task Planner for Poros Pilot
Uses Gemini to intelligently break down tasks
"""

import json
import os
from typing import List, Dict, Any
import google.generativeai as genai
from dataclasses import dataclass, asdict


@dataclass
class Task:
    """A single task step"""
    id: str
    action: str
    agent_capability: str = None
    parameters: Dict[str, Any] = None
    depends_on: List[str] = None
    reasoning: str = ""

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.depends_on is None:
            self.depends_on = []


class LLMTaskPlanner:
    """Intelligent task planner using Gemini"""

    def __init__(self, api_key: str = None):
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Use gemini-pro (more stable than gemini-1.5-flash)
        self.model = genai.GenerativeModel('gemini-pro')

    def create_plan(self, user_request: str) -> Dict:
        """Create an execution plan using LLM"""

        # Craft the planning prompt
        prompt = self._create_planning_prompt(user_request)

        try:
            # Get LLM response
            response = self.model.generate_content(prompt)

            # Parse JSON response
            plan_data = self._parse_llm_response(response.text)

            # Validate and enrich
            tasks = self._validate_tasks(plan_data.get("tasks", []))
            confidence = plan_data.get("confidence", 50.0)
            reasoning = plan_data.get("reasoning", "")

            return {
                "tasks": tasks,
                "confidence": confidence,
                "reasoning": reasoning,
                "raw_response": response.text
            }

        except Exception as e:
            print(f"❌ LLM Planning failed: {e}")
            # Fallback to simple plan
            return self._fallback_plan(user_request)

    def _create_planning_prompt(self, user_request: str) -> str:
        """Create the prompt for the LLM"""
        return f"""You are an intelligent task planner for a personal AI assistant.

Your job: Break down the user's request into executable steps.

Available agent capabilities:
- weather_forecast (get weather for any city)
- calendar_management (check availability, schedule events)
- email_operations (send emails, check inbox)
- web_search (research information)
- booking_services (book appointments, restaurants, travel)
- finance_operations (check balances, make payments)

User Request: "{user_request}"

Create a detailed execution plan. Return ONLY valid JSON in this EXACT format:

{{
  "reasoning": "Brief explanation of your plan",
  "confidence": 85.5,
  "tasks": [
    {{
      "id": "task_1",
      "action": "check_calendar",
      "agent_capability": "calendar_management",
      "parameters": {{"date": "2025-01-25", "time_range": "9am-5pm"}},
      "depends_on": [],
      "reasoning": "Why this step is needed"
    }},
    {{
      "id": "task_2",
      "action": "find_dentist",
      "agent_capability": "booking_services",
      "parameters": {{"specialty": "dentist", "location": "nearby"}},
      "depends_on": ["task_1"],
      "reasoning": "Why this step is needed"
    }}
  ]
}}

Confidence rules:
- 90-100%: Simple, clear request (e.g., "What's the weather?")
- 70-89%: Multi-step but straightforward (e.g., "Book dentist")
- 50-69%: Complex or requires user input (e.g., "Plan a trip")
- 0-49%: Unclear or impossible request

Return ONLY the JSON, no other text."""

    def _parse_llm_response(self, response_text: str) -> Dict:
        """Parse LLM response into structured data"""
        # Clean up response
        text = response_text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Parse JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error: {e}")
            print(f"Response was: {text[:200]}")
            raise

    def _validate_tasks(self, tasks_data: List[Dict]) -> List[Task]:
        """Convert dict tasks to Task objects"""
        tasks = []
        for i, task_dict in enumerate(tasks_data):
            task = Task(
                id=task_dict.get("id", f"task_{i+1}"),
                action=task_dict.get("action", "unknown"),
                agent_capability=task_dict.get("agent_capability"),
                parameters=task_dict.get("parameters", {}),
                depends_on=task_dict.get("depends_on", []),
                reasoning=task_dict.get("reasoning", "")
            )
            tasks.append(task)
        return tasks

    def _fallback_plan(self, user_request: str) -> Dict:
        """Fallback plan if LLM fails"""
        # Check for simple weather queries
        if any(word in user_request.lower() for word in ["weather", "temperature", "forecast"]):
            return {
                "reasoning": "Simple weather query (fallback)",
                "confidence": 85.0,
                "tasks": [
                    Task(
                        id="weather_1",
                        action="get_weather",
                        agent_capability="weather_forecast",
                        parameters={"city": "San Francisco"},
                        reasoning="Fetch weather information"
                    )
                ]
            }

        # Default: ask for clarification
        return {
            "reasoning": "Could not understand request (fallback)",
            "confidence": 30.0,
            "tasks": [
                Task(
                    id="clarify_1",
                    action="clarify",
                    parameters={"question": "I'm not sure what you want. Could you rephrase?"},
                    reasoning="Need more information from user"
                )
            ]
        }


# Test the planner
async def test_planner():
    """Test the LLM planner"""
    print("Testing LLM Task Planner...\n")

    planner = LLMTaskPlanner()

    test_requests = [
        "What's the weather in Tokyo?",
        "Book me a dentist appointment for next Tuesday",
        "Plan a weekend trip to Seattle",
    ]

    for request in test_requests:
        print(f"\n{'='*60}")
        print(f"Request: {request}")
        print('='*60)

        plan = planner.create_plan(request)

        print(f"\nReasoning: {plan['reasoning']}")
        print(f"Confidence: {plan['confidence']}%")
        print(f"\nTasks ({len(plan['tasks'])}):")

        for i, task in enumerate(plan['tasks'], 1):
            if isinstance(task, Task):
                print(f"\n  {i}. {task.action}")
                print(f"     Capability: {task.agent_capability}")
                print(f"     Parameters: {task.parameters}")
                if task.depends_on:
                    print(f"     Depends on: {task.depends_on}")
                print(f"     Reasoning: {task.reasoning}")
            else:
                print(f"\n  {i}. {task}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_planner())
