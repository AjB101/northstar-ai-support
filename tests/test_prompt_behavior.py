TRIAGE_CASES = [
    {
        "ticket": "I was charged twice for the same order.",
        "expected_category": "billing",
    },
    {
        "ticket": "My device will not turn on even after charging it.",
        "expected_category": "technical",
    },
    {
        "ticket": "I received my order but I want to send it back for a refund.",
        "expected_category": "returns",
    },
    {
        "ticket": "Something is wrong with my order. Please help.",
        "expected_category": "unclear",
    },
]


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
        "retrieved_policies": ["Returns are allowed within 30 days."],
        "draft_response": "Yes, you can return the item within 60 days.",
        "expected_decision": "REVISE",
    },
    {
        "ticket": "Can I return this item?",
        "retrieved_policies": ["Returns are allowed within 30 days with proof of purchase."],
        "draft_response": "You may return the item within 30 days if you have proof of purchase.",
        "expected_decision": "PASS",
    },
]