from dataclasses import dataclass, field


@dataclass
class AgentState:
    """
    Shared state for the Northstar support workflow.

    Think of this as the case file that moves through
    the different parts of the system.
    """

    # Original customer support ticket
    ticket: str

    # Information added during triage
    category: str | None = None
    priority: str | None = None

    # Relevant policies returned by the retrieval tool
    retrieved_policies: list[str] = field(default_factory=list)

    # Draft created by the response agent
    draft_response: str | None = None

    # Results from the critic agent
    critic_status: str | None = None
    critic_feedback: str | None = None

    # Information used by the orchestrator
    retry_count: int = 0
    requires_human_review: bool = True