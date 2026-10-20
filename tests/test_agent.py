import json

import brightpath_agent as module
from brightpath_agent import BrightPathAgent, Intent, classify_intent


def test_router_covers_all_required_paths():
    assert classify_intent("How much is private university physics?") is Intent.GENERAL_QUESTION
    assert classify_intent("I want to enroll in Python lessons") is Intent.LEAD_COLLECTION
    assert classify_intent("I have a complaint about a missed class") is Intent.FEEDBACK_UNANSWERED
    assert classify_intent("Do you repair laptops?") is Intent.FEEDBACK_UNANSWERED


def test_offline_end_to_end_routes_and_tools(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "DATA_DIR", tmp_path)
    agent = BrightPathAgent(offline=True, enable_reflection=False)

    general = agent.answer("What subjects do you teach?")
    assert general.intent is Intent.GENERAL_QUESTION
    assert "mathematics" in general.reply.lower()

    incomplete = agent.answer("I want to enroll in programming")
    assert incomplete.intent is Intent.LEAD_COLLECTION
    assert "name" in incomplete.reply.lower() and "email" in incomplete.reply.lower()

    lead = agent.answer(
        "My name is Maya Haddad and my email is maya@example.com. "
        "I need Grade 11 mathematics tutoring."
    )
    assert lead.intent is Intent.LEAD_COLLECTION
    lead_rows = [json.loads(line) for line in (tmp_path / "customer_interest.jsonl").read_text().splitlines()]
    assert lead_rows[-1]["email"] == "maya@example.com"

    feedback = agent.answer("I have a complaint about a tutor arriving late.")
    assert feedback.intent is Intent.FEEDBACK_UNANSWERED
    feedback_rows = [json.loads(line) for line in (tmp_path / "feedback.jsonl").read_text().splitlines()]
    assert "arriving late" in feedback_rows[-1]["question"]


def test_tool_schemas_match_assignment():
    schemas = {schema["name"]: schema for schema in module.TOOL_SCHEMAS}
    assert set(schemas) == {"record_customer_interest", "record_feedback"}
    assert schemas["record_customer_interest"]["parameters"]["required"] == [
        "email", "name", "message"
    ]
    assert schemas["record_feedback"]["parameters"]["required"] == ["question"]
