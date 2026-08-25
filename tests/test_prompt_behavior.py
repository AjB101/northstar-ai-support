import json

from app.triage_agent import TriageAgent


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)

    def invoke(self, messages):
        return FakeResponse(self.responses.pop(0))


TRIAGE_CASES = [
    {
        "ticket": "I was charged twice for the same order.",
        "llm_response": {
            "category": "billing",
            "issue_summary": "Customer reports being charged twice for one order.",
            "classification_confidence": 0.98,
        },
        "expected_category": "billing",
    },
    {
        "ticket": "My device will not turn on even after charging it.",
        "llm_response": {
            "category": "technical",
            "issue_summary": "Customer reports that the device will not power on.",
            "classification_confidence": 0.96,
        },
        "expected_category": "technical",
    },
    {
        "ticket": "I received my order but I want to send it back for a refund.",
        "llm_response": {
            "category": "returns",
            "issue_summary": "Customer wants to return an order for a refund.",
            "classification_confidence": 0.95,
        },
        "expected_category": "returns",
    },
    {
        "ticket": "Something is wrong with my order. Please help.",
        "llm_response": {
            "category": "unclear",
            "issue_summary": "Customer reports an unspecified problem with an order.",
            "classification_confidence": 0.35,
        },
        "expected_category": "unclear",
    },
]


def test_triage_agent_classifies_expected_categories():
    for case in TRIAGE_CASES:
        fake_llm = FakeLLM(
            [json.dumps(case["llm_response"])]
        )

        agent = TriageAgent(fake_llm)

        result = agent.classify(case["ticket"])

        assert result["category"] == case["expected_category"]
        assert "issue_summary" in result
        assert "classification_confidence" in result


def test_triage_agent_rejects_invalid_category():
    fake_llm = FakeLLM(
        [
            json.dumps(
                {
                    "category": "shipping",
                    "issue_summary": "Customer asks about shipping.",
                    "classification_confidence": 0.9,
                }
            )
        ]
    )

    agent = TriageAgent(fake_llm)

    result = agent.classify("Where is my package?")

    assert result["category"] == "unclear"
    assert result["classification_confidence"] == 0.0


def test_triage_agent_handles_invalid_json():
    fake_llm = FakeLLM(["This is not JSON"])

    agent = TriageAgent(fake_llm)

    result = agent.classify("I need help.")

    assert result == {
        "category": "unclear",
        "issue_summary": "Unable to classify the ticket reliably.",
        "classification_confidence": 0.0,
    }


def test_triage_agent_rejects_invalid_confidence():
    fake_llm = FakeLLM(
        [
            json.dumps(
                {
                    "category": "billing",
                    "issue_summary": "Customer reports a billing issue.",
                    "classification_confidence": 1.5,
                }
            )
        ]
    )

    agent = TriageAgent(fake_llm)

    result = agent.classify("I was billed incorrectly.")

    assert result["category"] == "unclear"
    assert result["classification_confidence"] == 0.0

RESPONSE_GROUNDING_CASES = [
    {
        "ticket": "Can I return this item after 60 days?",
        "retrieved_policies": [],
        "expected_behavior": "Do not invent a return deadline.",
    },
    {
        "ticket": "Will I get a full refund?",
        "retrieved_policies": [],
        "expected_behavior": "Do not promise a refund without supporting policy.",
    },
]


CRITIC_CASES = [
    {
        "ticket": "Can I return this item after 60 days?",
        "retrieved_policies": [
            "Returns are allowed within 30 days."
        ],
        "draft_response": (
            "Yes, you can return the item within 60 days."
        ),
        "expected_decision": "REVISE",
    },
    {
        "ticket": "Can I return this item?",
        "retrieved_policies": [
            "Returns are allowed within 30 days with proof of purchase."
        ],
        "draft_response": (
            "You may return the item within 30 days "
            "if you have proof of purchase."
        ),
        "expected_decision": "PASS",
    },
]