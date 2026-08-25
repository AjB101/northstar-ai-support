import json

from app.prompts import TRIAGE_SYSTEM_PROMPT


class TriageAgent:
    """Classifies incoming support tickets for the Northstar workflow."""

    VALID_CATEGORIES = {
        "billing",
        "technical",
        "returns",
        "unclear",
    }

    def __init__(self, llm):
        self.llm = llm

    def classify(self, ticket: str) -> dict:
        messages = [
            ("system", TRIAGE_SYSTEM_PROMPT),
            (
                "human",
                f"""Customer ticket:
{ticket}

Classify this ticket according to the system instructions.""",
            ),
        ]

        raw = self.llm.invoke(messages).content.strip()

        try:
            cleaned = (
                raw.replace("```json", "")
                .replace("```", "")
                .strip()
            )
            result = json.loads(cleaned)
        except (json.JSONDecodeError, TypeError):
            return self._fallback()

        if not isinstance(result, dict):
            return self._fallback()

        category = result.get("category")
        summary = result.get("issue_summary")
        confidence = result.get("classification_confidence")

        if category not in self.VALID_CATEGORIES:
            return self._fallback()

        if not isinstance(summary, str) or not summary.strip():
            return self._fallback()

        if not isinstance(confidence, (int, float)):
            return self._fallback()

        if not 0.0 <= float(confidence) <= 1.0:
            return self._fallback()

        return {
            "category": category,
            "issue_summary": summary.strip(),
            "classification_confidence": float(confidence),
        }

    @staticmethod
    def _fallback() -> dict:
        return {
            "category": "unclear",
            "issue_summary": "Unable to classify the ticket reliably.",
            "classification_confidence": 0.0,
        }