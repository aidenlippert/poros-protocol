"""
Intelligent Client Agent - Powered by Gemini

This agent acts as the user-facing interface that:
1. Understands natural language requests
2. Discovers and reads agent cards from Poros Protocol
3. Intelligently selects the best agent for the task
4. Asks for clarification when needed
5. Calls agents and formats responses for users
6. Remembers conversation context and user preferences
"""

import os
import json
import httpx
import google.generativeai as genai
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Use the correct model name for the current API
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

POROS_API_URL = os.getenv("POROS_API_URL", "https://poros-protocol-production.up.railway.app")


class IntelligentClient:
    """
    Gemini-powered client that understands user intent and orchestrates agent calls
    """

    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
        self.discovered_agents = []

    async def discover_agents(self) -> List[Dict]:
        """Fetch all available agents from Poros Protocol"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{POROS_API_URL}/api/registry/agents")
            self.discovered_agents = response.json()
            return self.discovered_agents

    def format_agents_for_llm(self, agents: List[Dict]) -> str:
        """Format agent cards in a way Gemini can understand"""
        if not agents:
            return "No agents currently available in the marketplace."

        formatted = "Available agents in the Poros Protocol marketplace:\n\n"
        for agent in agents:
            card = agent.get("agent_card", {})
            formatted += f"Agent: {card.get('name')}\n"
            formatted += f"ID: {agent.get('agent_id')}\n"
            formatted += f"Description: {card.get('description')}\n"
            formatted += f"URL: {card.get('url')}\n"

            skills = card.get('skills', [])
            if skills:
                formatted += "Skills:\n"
                for skill in skills:
                    formatted += f"  - {skill.get('name')}: {skill.get('description')}\n"
                    formatted += f"    Input: {skill.get('input_schema')}\n"
                    formatted += f"    Output: {skill.get('output_schema')}\n"

            pricing = card.get('pricing', {})
            if pricing:
                formatted += f"Pricing: ${pricing.get('amount')} per {pricing.get('model')}\n"

            formatted += "\n---\n\n"

        return formatted

    async def understand_request(self, user_message: str) -> Dict:
        """
        Use Gemini to understand what the user wants and determine if we need:
        - More information from the user
        - To call a specific agent
        - To search for agents
        """
        # Get available agents
        await self.discover_agents()
        agents_info = self.format_agents_for_llm(self.discovered_agents)

        # Build conversation context
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.conversation_history[-5:]  # Last 5 messages for context
        ])

        # Gemini prompt
        prompt = f"""You are an intelligent assistant that helps users interact with a marketplace of AI agents.

{agents_info}

Conversation history:
{history_text}

User's new message: "{user_message}"

Your task:
1. Understand what the user wants
2. Determine if you have enough information to proceed
3. If not, ask clarifying questions
4. If yes, identify which agent(s) can help and what parameters to send

Respond in JSON format:
{{
    "intent": "search_hotels|ask_clarification|call_agent|general_chat",
    "confidence": 0.0-1.0,
    "clarification_needed": true/false,
    "clarification_question": "What question to ask user",
    "selected_agent_id": "agent_id if ready to call",
    "agent_parameters": {{"param": "value"}},
    "reasoning": "Why you made this decision",
    "user_friendly_response": "Natural language response to show the user"
}}
"""

        response = model.generate_content(prompt)

        try:
            # Parse Gemini's JSON response
            result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            return result
        except json.JSONDecodeError:
            # Fallback if Gemini doesn't return valid JSON
            return {
                "intent": "general_chat",
                "confidence": 0.5,
                "clarification_needed": False,
                "user_friendly_response": response.text
            }

    async def call_agent(self, agent_id: str, parameters: Dict) -> Dict:
        """Call the selected agent through Poros orchestrator"""
        # Extract skill tags from agent
        agent = next((a for a in self.discovered_agents if a.get("agent_id") == agent_id), None)
        if not agent:
            return {"error": "Agent not found"}

        skills = agent.get("agent_card", {}).get("skills", [])
        skill_names = [skill.get("name") for skill in skills]

        # Build query for orchestrator
        query = json.dumps(parameters)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{POROS_API_URL}/api/orchestrator/orchestrate",
                json={
                    "query": query,
                    "skill_tags": skill_names,
                    "max_agents": 1
                }
            )
            return response.json()

    async def process_message(self, user_message: str) -> str:
        """Main entry point - process a user message and return a response"""
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Understand the request
        understanding = await self.understand_request(user_message)

        # If clarification needed, ask the user
        if understanding.get("clarification_needed"):
            response = understanding.get("user_friendly_response",
                                       understanding.get("clarification_question",
                                                       "Can you provide more details?"))
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            return response

        # If ready to call agent
        if understanding.get("intent") == "call_agent" and understanding.get("selected_agent_id"):
            agent_id = understanding["selected_agent_id"]
            parameters = understanding.get("agent_parameters", {})

            # Call the agent
            agent_response = await self.call_agent(agent_id, parameters)

            # Format response for user using Gemini
            format_prompt = f"""The user asked: "{user_message}"

We called agent "{agent_id}" and got this response:
{json.dumps(agent_response, indent=2)}

Format this in a friendly, natural way for the user. Be concise and helpful."""

            formatted = model.generate_content(format_prompt)
            response = formatted.text

            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            return response

        # General chat or other intents
        response = understanding.get("user_friendly_response", "I'm here to help! What can I do for you?")
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        return response


# Example usage
async def main():
    client = IntelligentClient()

    print("🤖 Intelligent Poros Client Agent")
    print("=" * 50)
    print("I can help you discover and interact with agents!")
    print("=" * 50)
    print()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        response = await client.process_message(user_input)
        print(f"\n🤖 Assistant: {response}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
