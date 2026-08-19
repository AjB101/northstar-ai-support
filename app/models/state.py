from dataclasses import dataclass, field


@dataclass
class AgentState:
    """
    Shared state passed through the Northstar multi-agent workflow.

    Think of this as the case file that travels through
    triage, retrieval, response generation, critic review,
    retries, and human review.
    """

    # Original customer ticket
    ticket: str

    # -------------------------
    # Triage Agent output
    # -------------------------
    category: str | None = None
    issue_summary: str | None = None
    classification_confidence: float | None = None

    # -------------------------
    # ChromaDB retrieval output
    # -------------------------
    retrieved_policies: list[str] = field(default_factory=list)

    # -------------------------
    # Response Agent output
    # -------------------------
    draft_response: str | None = None
    policy_used: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)

    # -------------------------
    # Critic Agent output
    # -------------------------
    critic_decision: str | None = None
    unsupported_claims: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    correction_instructions: list[str] = field(default_factory=list)

    # -------------------------
    # Orchestration state
    # -------------------------
    retry_count: int = 0
    requires_human_review: bool = False