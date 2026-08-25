import json

from app.models.state import AgentState
from app.triage_agent import TriageAgent
from app.critic_agent import (
    llm,
    retrieve_policy,
    response_agent,
    critic_reviewer,
)


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
    Retry when the Critic requests revision
    and retry attempts are still available.
    """
    return (
        state.critic_decision == "REVISE"
        and state.retry_count < MAX_RETRIES
    )


def finalize_workflow(state: AgentState) -> AgentState:
    """
    Escalate a response that never passes Critic review.
    """
    if state.critic_decision != "PASS":
        state.requires_human_review = True

    return state


def run_workflow(ticket: str) -> AgentState:
    """
    Run a customer ticket through the Northstar workflow:

    Triage -> Retrieval -> Response -> Critic
                       -> Retry if needed
                       -> Human review if retries fail
    """

    state = AgentState(ticket=ticket)

    # 1. TRIAGE
    triage_agent = TriageAgent(llm)
    triage_result = triage_agent.classify(ticket)

    state.category = triage_result["category"]
    state.issue_summary = triage_result["issue_summary"]
    state.classification_confidence = triage_result[
        "classification_confidence"
    ]

    # 2. POLICY RETRIEVAL
    policy_result = retrieve_policy(ticket)

    policy_text = policy_result["policy_text"]
    state.retrieved_policies = [policy_text]

    # 3. RESPONSE + CRITIC LOOP
    while True:
        raw_response = response_agent.generate(
            ticket=state.ticket,
            policy=policy_text,
            correction_instructions=state.correction_instructions,
        )

        # Normalize the Response Agent's JSON output
        # into the shared AgentState fields.
        try:
            cleaned_response = (
                raw_response
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )
            response_result = json.loads(cleaned_response)

        except (json.JSONDecodeError, TypeError):
            response_result = {
                "draft_response": raw_response,
                "policy_used": [],
                "unresolved_questions": [
                    "Response Agent returned invalid structured output."
                ],
            }

        state.draft_response = str(
            response_result.get(
                "draft_response",
                raw_response,
            )
        )
        
        state.policy_used = response_result.get(
            "policy_used",
            [],
        )
        state.unresolved_questions = response_result.get(
            "unresolved_questions",
            [],
        )

        # 4. CRITIC REVIEW
        critic_result = critic_reviewer.evaluate(
            ticket=state.ticket,
            policy=policy_text,
            draft=state.draft_response,
            retry_count=state.retry_count,
        )

        state.critic_decision = critic_result["critic_decision"]
        state.unsupported_claims = critic_result.get(
            "unsupported_claims",
            [],
        )
        state.missing_information = critic_result.get(
            "missing_information",
            [],
        )
        state.correction_instructions = critic_result.get(
            "correction_instructions",
            [],
        )

        request_human_review(
            state,
            critic_result.get(
                "requires_human_review",
                False,
            ),
        )

        # Critic approved the response.
        if state.critic_decision == "PASS":
            break

        # Critic rejected it, but another attempt is available.
        if should_retry(state):
            state.retry_count += 1
            continue

        # No retries remain.
        break

    return finalize_workflow(state)