from app.models.state import AgentState


MAX_RETRIES = 2


def run_workflow(ticket: str) -> AgentState:
    """
    Start a customer support ticket through
    the Northstart multi-agent workflow.
    """


    state = AgentState(ticket=ticket)

    return state