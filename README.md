# BrightPath Tutoring Agent

BrightPath Tutoring is a fictional tutoring-center assistant built for the C3 Introduction to Agents assignment. It answers business questions, recommends tutoring options, collects qualified leads, records complaints and unanswered questions, preserves short-term chat history, and runs in a Gradio chat interface.

## Assignment requirements covered

- Business identity in `me/about_business.pdf` and `me/business_summary.txt`
- Clearly separated `PERSONA` and `INSTRUCTIONS` in `brightpath_agent.py` and the notebook
- Three-way router: general question, lead collection, feedback/unanswered question
- MCP-style schemas for `record_customer_interest(email, name, message)` and `record_feedback(question)`
- Actual Gemini function calling through the current `google-genai` Python SDK
- Short-term history passed with each message
- Gradio `ChatInterface`
- Bonus reflection step that logs the original draft and revised reply
- Automated tests and a live smoke test

## Setup

Python 3.10 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add a free-tier Google AI Studio key to `.env`:

```text
GEMINI_API_KEY=your_real_key
GEMINI_MODEL=gemini-3.5-flash-lite
ENABLE_REFLECTION=true
```

The real `.env` is ignored by Git. Never put a key in the notebook or repository.

## Run

```bash
python app.py
```

Open the local Gradio URL printed in the terminal.

## Submission video

A finished narrated 1080p demonstration is included at:

```text
output/video/brightpath_tutoring_demo.mp4
```

It presents the business identity, router, general questions, recommendations,
both verified tool calls, reflection, Gradio verification, tests, and secret safety.
To regenerate it locally:

```bash
python scripts/create_demo_video.py
```

## Test

Run deterministic local tests:

```bash
pytest -q
```

Run the real Gemini end-to-end smoke test:

```bash
python scripts/smoke_test_live.py
```

The live test verifies all three routes, both tools, chat-history input, and the reflection log. It uses only the configured Gemini model and has no paid fallback.

## Runtime records

The tools create local JSON Lines files under `data/`:

- `customer_interest.jsonl`
- `feedback.jsonl`
- `reflections.jsonl`

These runtime records are ignored by Git so personal information is not accidentally submitted. For a classroom demonstration, show the terminal tool-call messages or use fictional test data.

## Safe demonstration sequence

1. Ask: `What mathematics tutoring and prices do you offer for Grade 11?`
2. Ask for advice: `I am a first-year engineering student struggling with mechanics. What should I choose?`
3. Start a lead: `I want to enroll in private physics tutoring.`
4. Complete it with fictional details: `My name is Maya Haddad and my email is maya.haddad@example.com. I am in Grade 12 and prefer Saturday mornings.`
5. Leave feedback: `I have a complaint: a tutor arrived late. Please record this.`
6. Show the router, tool, and reflection messages in the terminal.

## Important limitations

- The business, people, address, telephone number, and email are fictional.
- A lead record is not a confirmed booking.
- Tutor availability always requires staff confirmation.
- Free-tier quotas and model availability are controlled by Google.
