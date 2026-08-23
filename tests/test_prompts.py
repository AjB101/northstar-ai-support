from app.models.state import AgentState
from app.prompts import (
    TRIAGE_SYSTEM_PROMPT,
    RESPONSE_SYSTEM_PROMPT,
    CRITIC_SYSTEM_PROMPT,
)


def test_triage_prompt_matches_agent_state():
    assert "category" in TRIAGE_SYSTEM_PROMPT
    assert "issue_summary" in TRIAGE_SYSTEM_PROMPT
    assert "classification_confidence" in TRIAGE_SYSTEM_PROMPT


def test_response_prompt_matches_agent_state():
    assert "draft_response" in RESPONSE_SYSTEM_PROMPT
    assert "policy_used" in RESPONSE_SYSTEM_PROMPT
    assert "unresolved_questions" in RESPONSE_SYSTEM_PROMPT


def test_response_prompt_requires_policy_grounding():
    assert "retrieved company policies" in RESPONSE_SYSTEM_PROMPT
    assert "Do not invent company policy" in RESPONSE_SYSTEM_PROMPT


def test_critic_prompt_matches_agent_state():
    assert "critic_decision" in CRITIC_SYSTEM_PROMPT
    assert "unsupported_claims" in CRITIC_SYSTEM_PROMPT
    assert "missing_information" in CRITIC_SYSTEM_PROMPT
    assert "correction_instructions" in CRITIC_SYSTEM_PROMPT


def test_critic_prompt_defines_review_decisions():
    assert "PASS" in CRITIC_SYSTEM_PROMPT
    assert "REVISE" in CRITIC_SYSTEM_PROMPT


def test_prompt_fields_exist_in_agent_state():
    state_fields = AgentState.__dataclass_fields__

    expected_fields = [
        "category",
        "issue_summary",
        "classification_confidence",
        "draft_response",
        "policy_used",
        "unresolved_questions",
        "critic_decision",
        "unsupported_claims",
        "missing_information",
        "correction_instructions",
    ]

    for field in expected_fields:
        assert field in state_fields