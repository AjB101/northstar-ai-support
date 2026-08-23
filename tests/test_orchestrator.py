from app.models.state import AgentState
from app.orchestrator import (
    MAX_RETRIES,
    finalize_workflow,
    request_human_review,
    should_retry,
)


def test_retry_when_critic_requests_revision():
    """
    A response should retry when the Critic says REVISE
    and retry attempts are still available.
    """
    state = AgentState(
        ticket="Test ticket",
        critic_decision="REVISE",
        retry_count=0,
    )

    assert should_retry(state) is True


def test_no_retry_when_limit_reached():
    """
    A response should not retry after reaching MAX_RETRIES.
    """
    state = AgentState(
        ticket="Test ticket",
        critic_decision="REVISE",
        retry_count=MAX_RETRIES,
    )

    assert should_retry(state) is False


def test_no_retry_when_critic_passes():
    """
    A response that passes Critic review should not retry.
    """
    state = AgentState(
        ticket="Test ticket",
        critic_decision="PASS",
        retry_count=0,
    )

    assert should_retry(state) is False


def test_failed_final_response_requires_human_review():
    """
    A response that finishes without PASS should
    be escalated for human review.
    """
    state = AgentState(
        ticket="Test ticket",
        critic_decision="REVISE",
        retry_count=MAX_RETRIES,
    )

    result = finalize_workflow(state)

    assert result.requires_human_review is True


def test_passed_response_does_not_require_human_review():
    """
    A response that passes Critic review should finish
    without requiring human review.
    """
    state = AgentState(
        ticket="Test ticket",
        critic_decision="PASS",
    )

    result = finalize_workflow(state)

    assert result.requires_human_review is False


def test_human_review_request_is_preserved():
    """
    Once human review is requested, a later False value
    should not remove that request.
    """
    state = AgentState(
        ticket="Test ticket",
        requires_human_review=True,
    )

    request_human_review(
        state,
        agent_requires_human_review=False,
    )

    assert state.requires_human_review is True