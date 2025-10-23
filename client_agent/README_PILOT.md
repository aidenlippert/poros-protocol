# Poros Pilot - Testing Guide

## 🚀 What is Poros Pilot?

**Your LLM-powered personal AI assistant** that:
- Understands natural language requests
- Plans multi-step workflows intelligently
- Knows when to ask for your approval
- Executes tasks autonomously when safe
- Works with agents from the Poros Protocol network

## 🧠 The Intelligence

**3-Layer Architecture**:
1. **Gemini AI** - Understands your request, plans tasks, scores confidence
2. **Poros Pilot** - Orchestrates execution, manages approval gates
3. **Poros Protocol** - Discovers and routes to specialist agents

## ⚙️ Setup

### 1. Get a Gemini API Key

Go to: https://makersuite.google.com/app/apikey

Create a free API key.

### 2. Set the API Key

**Windows**:
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/Mac**:
```bash
export GEMINI_API_KEY=your_api_key_here
```

### 3. Install Dependencies

```bash
cd c:/Users/aiden/poros-protocol/client_agent
pip install google-generativeai httpx
```

## 🧪 Run the Tests

### Quick Test (Automated)

```bash
python test_pilot.py
```

This will test:
1. ✅ Weather query (AUTO mode - instant execution)
2. ✅ Book dentist (CONFIRM mode - shows plan, asks approval)

### Interactive Mode

```bash
python poros_pilot.py
```

Then try these commands:

**Simple (AUTO execution)**:
```
You: What's the weather in Tokyo?
```
Expected: Executes immediately, shows weather

**Multi-step (CONFIRM mode)**:
```
You: Book me a dentist appointment for next Tuesday
```
Expected:
1. Shows AI reasoning
2. Shows confidence score (60-70%)
3. Displays execution plan
4. Asks for your approval
5. Executes if you approve

**Complex (INTERACTIVE mode)**:
```
You: Plan a weekend trip to Seattle
```
Expected: Asks clarifying questions

## 📊 The 4 Approval Modes

| Confidence | Mode | Behavior | Example |
|------------|------|----------|---------|
| 90-100% | AUTO | Just does it | "What's the weather?" |
| 70-89% | NOTIFY | Does it, tells you | "Send email to John" |
| 50-69% | CONFIRM | Shows plan, asks first | "Book dentist" |
| 0-49% | INTERACTIVE | Needs your help | "Plan my life" |

## 🎯 Example Sessions

### Session 1: Weather (AUTO)

```
You: What's the weather in Tokyo?

============================================================
Request: What's the weather in Tokyo?
============================================================

AI Reasoning: Simple weather query for Tokyo
Confidence: 95.0%
Approval Mode: auto

✅ High confidence - executing automatically...

🚀 Executing...

[1/1] get_weather...
   ✓ Done

✅ Completed!

   Tokyo: 72°F, Partly Cloudy
```

### Session 2: Book Dentist (CONFIRM)

```
You: Book me a dentist appointment for next Tuesday

============================================================
Request: Book me a dentist appointment for next Tuesday
============================================================

AI Reasoning: Multi-step booking requiring calendar check and agent discovery
Confidence: 65.0%
Approval Mode: confirm

⏸️  Requesting your approval...

📝 Execution Plan:
------------------------------------------------------------
  1. check_calendar
     Agent: calendar_management
     Params: {'date': '2025-01-28', 'time_range': 'business_hours'}
     Why: Need to verify user is available on Tuesday

  2. find_dentist
     Agent: booking_services
     Params: {'specialty': 'dentist', 'location': 'nearby', 'date': '2025-01-28'}
     Why: Locate available dentists

  3. book_appointment (after: check_calendar, find_dentist)
     Agent: booking_services
     Params: {'service': 'dentist', 'date': '2025-01-28'}
     Why: Finalize the appointment booking
------------------------------------------------------------

✅ Approve? [Y/n]: y

🚀 Executing...

[1/3] check_calendar...
   ✓ Done

[2/3] find_dentist...
   ✓ Done

[3/3] book_appointment...
   ✓ Done

✅ Completed!
```

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
Set the environment variable as shown in Setup step 2.

### "404 models/gemini-pro is not found"
Your API key might not have access. Try:
1. Check your API key is valid
2. Enable the Gemini API in Google Cloud Console
3. Wait a few minutes if just created

### "LLM Planning: DISABLED"
The system falls back to pattern matching. Weather queries will still work.

## 📝 What's Next?

Now that you've tested the core engine, you can:

1. **Add More Agents** - Email, calendar, research, finance
2. **Build FastAPI Wrapper** - Make it accessible via web
3. **Create Web UI** - Beautiful interface in the portal
4. **Integrate Swarms** - Even smarter multi-agent reasoning
5. **Add Memory** - Remember user preferences

## 🎯 The Vision

**Fully autonomous personal assistant** that handles:
- 📅 Scheduling (dentist, meetings, reminders)
- ✈️ Travel planning (flights, hotels, activities)
- 📧 Email management (triage, responses, summaries)
- 💰 Finance (bill pay, budgets, tracking)
- 🔬 Research (web search, summaries, analysis)

All while keeping you in control through smart approval gates!

---

**Ready to test?** Run `python test_pilot.py`! 🚀
