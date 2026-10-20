"""Small live test that verifies Gemini, routing, tools, memory input, and reflection."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from brightpath_agent import BrightPathAgent


DATA_DIR = ROOT / "data"


def count_rows(name: str) -> int:
    path = DATA_DIR / name
    return len(path.read_text(encoding="utf-8").splitlines()) if path.exists() else 0


def main() -> None:
    before_leads = count_rows("customer_interest.jsonl")
    before_feedback = count_rows("feedback.jsonl")
    before_reflections = count_rows("reflections.jsonl")

    agent = BrightPathAgent(enable_reflection=True)
    history = []
    prompts = [
        "What mathematics tutoring and prices do you offer for Grade 11?",
        (
            "My name is Maya Haddad and my email is maya.haddad@example.com. "
            "I need private Grade 11 mathematics tutoring on weekday evenings."
        ),
        "I have a complaint: a tutor arrived late. Please record this for your staff.",
    ]

    for prompt in prompts:
        result = agent.answer(prompt, history)
        print(json.dumps({"intent": result.intent.value, "reply": result.reply}, ensure_ascii=True))
        history.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": result.reply},
        ])

    assert count_rows("customer_interest.jsonl") > before_leads, "Lead tool was not called"
    assert count_rows("feedback.jsonl") > before_feedback, "Feedback tool was not called"
    assert count_rows("reflections.jsonl") >= before_reflections + 3, "Reflection was not logged"
    print("LIVE_SMOKE_TEST=PASS")


if __name__ == "__main__":
    main()
