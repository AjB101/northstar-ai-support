import json
import os

from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.prompts import (
    CRITIC_SYSTEM_PROMPT,
    RESPONSE_SYSTEM_PROMPT,
)
from app.chromadb_policy_tool import ( 
    initialize_policy_vector_db,
    fetch_rule_for_ticket, 
) 
from app.northstar_audit_logger import audit_logger

load_dotenv()
#retrieves deepseek key details from .env
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL","deepseek-v4-flash")

llm = ChatOpenAI(
    model=DEEPSEEK_MODEL,
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    temperature=0,
)

_policy_collection = initialize_policy_vector_db()
def retrieve_policy(ticket: str) -> Dict[str, Any]:
    """
    Retrieve the most relevant Northstar policy for the ticket.

    Returns:
        Dictionary containing:
            - policy_text
            - metadata
    """

    policy_result = fetch_rule_for_ticket(
        _policy_collection,
        ticket,
    )

    if not policy_result:
        return {
            "policy_text": (
                "No matching Northstar policy was found."
            ),
            "metadata": {},
        }

    return policy_result






class ResponseAgent:
    """
    Generates a customer-facing response using:
    - the original customer ticket
    - policy text retrieved by the shared retrieval tool
    - Critic correction instructions during retries

    This class does NOT retrieve policies itself.
    The orchestrator/shared retrieval tool is responsible
    for supplying the policy text.
    """

    def __init__(self, llm):
        self.llm = llm

    def generate(
        self,
        ticket: str,
        policy: str,
        correction_instructions: List[str] | None = None,
    ) -> str:
        """
        Generate a customer response.

        correction_instructions are supplied by the Critic
        when a previous response failed evaluation.
        """

        corrections = (
            "\n".join(
                f"- {instruction}"
                for instruction in correction_instructions
            )
            if correction_instructions
            else "None"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    RESPONSE_SYSTEM_PROMPT,
                ),
                (
                    "human",
                    """Customer ticket:
{ticket}

Retrieved policy evidence:
{policy}

Critic correction instructions:
{corrections}

Write only the proposed customer reply.

If Critic correction instructions are provided, use them
to revise and improve the response while remaining
consistent with the retrieved policy evidence.

Do not mention the Critic, QA process, retry process,
or correction instructions in the customer reply.""",
                ),
            ]
        )

        response = (prompt | self.llm).invoke(
            {
                "ticket": ticket,
                "policy": policy,
                "corrections": corrections,
            }
        )

        return response.content.strip()

class PolicyChecker:
    """Fast deterministic checks for explicit unsafe/unsupported wording."""

    FORBIDDEN_PHRASES = [
        "guaranteed refund",
        "guarantee a refund",
        "guaranteed replacement",
        "I promise you",
        "definitely get a refund",
    ]
    def check(self, draft: str) -> Dict[str, Any]:
        lower = draft.lower()
        violations = [
            f"Forbidden phrase: {phrase}"
            for phrase in self.FORBIDDEN_PHRASES
            if phrase.lower() in lower
        ]
        return {
            "ok": len(violations) == 0,
            "violations": violations,
        }

class CriticReviewer:
    """LLM QA critic. It evaluates; it does not rewrite the customer's reply."""

    def __init__(
        self,
        llm,
        policy_checker: PolicyChecker,
        audit_logger=None,
    ):
        self.llm = llm
        self.policy_checker = policy_checker
        self.audit_logger = audit_logger

    def evaluate(
        self,
        ticket: str,
        policy: str,
        draft: str,
        retry_count: int,
    ) -> Dict[str, Any]:
        """
        Evaluate a generated customer response.

        retry_count is supplied by the orchestrator and is
        recorded for every Critic evaluation.
        """
# Runs deterministic checks
        deterministic = self.policy_checker.check(draft)
        violations = (
            deterministic["violations"]
            if deterministic["violations"]
            else "None"
        )

# imports and fills out Critic prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    CRITIC_SYSTEM_PROMPT,
                ),
                (
                    "human",
                    """Original ticket:
{ticket}

Retrieved policy evidence:
{policy}

Draft response:
{draft}

Retry number:
{retry_count}

Deterministic policy-check violations:
{violations}""",
                ),
            ]
        )

#requests LLM to evaluate the proposal
        raw = (
            (prompt | self.llm).invoke(
                {
                    "ticket": ticket,
                    "policy": policy,
                    "draft": draft,
                    "retry_count": retry_count,
                    "violations": violations,
                }
            )
            .content
            .strip()
        )

# structures the Critic output
        try:
            cleaned = (
                raw
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            result = {
                "critic_decision": "REVISE",
                "score": 0,
                "issues": [
                    "Critic returned invalid structured output."
                ],
                "unsupported_claims": [],
                "missing_information": [],
                "correction_instructions": [
                    "Regenerate the response and ensure it "
                    "follows the supplied policy."
                ],
                "reason": (
                    "QA critic output could not be "
                    "parsed safely."
                ),
            }

# Make's sure Critic result is a dictionary
        if not isinstance(result, dict):
            result = {
                "critic_decision": "REVISE",
                "score": 0,
                "issues": [
                    "Critic returned an invalid result."
                ],
                "unsupported_claims": [],
                "missing_information": [],
                "correction_instructions": [
                    "Regenerate the response using only "
                    "the supplied policy evidence."
                ],
                "reason": "Invalid Critic result format.",
            }

# Ensures all expected fields exist
        result.setdefault(
            "critic_decision",
            "REVISE",
        )
        result.setdefault(
            "score",
            0,
        )
        result.setdefault(
            "issues",
            [],
        )
        result.setdefault(
            "unsupported_claims",
            [],
        )
        result.setdefault(
            "missing_information",
            [],
        )
        result.setdefault(
            "correction_instructions",
            [],
        )
        result.setdefault(
            "reason",
            "",
        )

# deterministic violations
        if deterministic["violations"]:
            result["critic_decision"] = "REVISE"
            for violation in deterministic["violations"]:
                if violation not in result["issues"]:
                    result["issues"].append(
                        violation
                    )
            correction = (
                "Remove all forbidden or unsupported "
                "guarantee language."
            )
            if correction not in result[
                "correction_instructions"
            ]:
                result[
                    "correction_instructions"
                ].append(
                    correction
                )

#human review field name matched
        result["requires_human_review"] = False
        result["retry_count"] = retry_count



# Audit logging for EVERY Critic evaluation.
        if self.audit_logger:
            self.audit_logger.log(
                {
                    "event": "critic_evaluation",
                    "critic_decision": result[
                        "critic_decision"
                    ],
                    "score": result.get(
                        "score",
                        0,
                    ),
                    "retry_count": retry_count,
                    "issues": result.get(
                        "issues",
                        [],
                    ),
                    "correction_instructions": result.get(
                        "correction_instructions",
                        [],
                    ),
                }
            )
        return result

policy_checker = PolicyChecker()
response_agent = ResponseAgent(llm)
critic_reviewer = CriticReviewer(
    llm=llm,
    policy_checker = policy_checker,
    audit_logger=audit_logger,
)
