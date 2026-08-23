from app.models.state import AgentState


MAX_RETRIES = 2

def request_human_review(
    state: AgentState,
    agent_requires_human_review: bool,
) -> None:
    """
    Preserve a human-review request once any agent raises it.
    """

    state.requires_human_review = (
        state.requires_human_review
        or agent_requires_human_review
    )


def should_retry(state: AgentState) -> bool:
    """
    Decide whether a revised response should be attempted.
    """

    return (
        state.critic_decision == "REVISE"
        and state.retry_count < MAX_RETRIES
    )


def finalize_workflow(state: AgentState) -> AgentState:
    """
    Escalate cases that do not pass critic review.
    """

    if state.critic_decision != "PASS":
        state.requires_human_review = True

    return state





def run_workflow(ticket: str) -> AgentState:
    """
    Start a customer support ticket through
    the Northstart multi-agent workflow.
    """


    state = AgentState(ticket=ticket)

    return state