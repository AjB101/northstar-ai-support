# Northstar AI Support

Northstar AI Support is a multi-agent AI customer support system developed for TEPP Phase 2. The system automates ticket triage, policy retrieval, response generation, and quality review while preserving human oversight for cases the AI cannot safely resolve.

## Business Problem

Northstar Support Co. currently relies on human support agents to manually:

1. Classify incoming customer tickets
2. Locate relevant company policies
3. Draft customer responses
4. Review responses before they are sent

This process can become slow and difficult to scale as ticket volume increases.

Northstar AI Support explores how multiple specialized AI agents can work together to automate routine parts of this workflow while maintaining policy grounding and human oversight.

## Architecture

The Northstar workflow is:

Customer Ticket  
→ Triage Agent  
→ Policy Retrieval (ChromaDB)  
→ Response Agent  
→ Critic Agent  
→ PASS or REVISE  
→ Human Review if the retry limit is reached

### Triage Agent

The Triage Agent identifies the type of customer issue and produces:

- `category`
- `issue_summary`
- `classification_confidence`

### Policy Retrieval

ChromaDB retrieves relevant Northstar company policy information based on the customer ticket.

### Response Agent

The Response Agent uses the customer ticket and retrieved policy to create a customer-facing response.

It produces:

- `draft_response`
- `policy_used`
- `unresolved_questions`

### Critic Agent

The Critic Agent acts as the quality-control reviewer.

It checks the proposed response for:

- Accuracy
- Relevance
- Policy grounding
- Unsupported claims
- Missing information

The Critic returns:

- `PASS` — the response passes review
- `REVISE` — the response requires correction

### Orchestrator

The Python orchestrator coordinates the agents and manages information passed between them through the shared `AgentState`.

The orchestrator controls the workflow:

Triage → Retrieval → Response → Critic

If the Critic returns `REVISE`, the response can be regenerated using the Critic's correction instructions.

The workflow allows up to two revision attempts. If the response still does not pass Critic review, the case is escalated for human review.

### Audit Logging

The system records important workflow events for observability and review, including:

- Workflow start
- Triage results
- Policy retrieval
- Critic evaluations
- Retry information
- Human-review status
- Workflow completion

Audit information can be exported to `final_agent_audit.json`.

## Setup

### 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a local `.env` file:

```text
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
```

Do not commit the `.env` file or API keys to GitHub.

## Run Tests

Run:

```powershell
pytest -v
```

Current test suite:

- 16 tests
- Orchestrator routing tests
- Triage behavioral tests
- Prompt contract tests

## Run the Workflow

Example:

```powershell
python -c "from app.orchestrator import run_workflow; s=run_workflow('I was charged twice for the same purchase.'); print(s)"
```

## Human Oversight

Northstar automates routine ticket classification, policy retrieval, response drafting, and quality review.

Human review is intentionally preserved as the final safety checkpoint when the Critic continues to reject a response after the allowed retry attempts.

This prevents unresolved or insufficiently grounded responses from being automatically approved.

## Project Structure

```text
northstar-ai-support/
├── app/
│   ├── models/
│   │   └── state.py
│   ├── prompts/
│   ├── triage_agent.py
│   ├── critic_agent.py
│   ├── orchestrator.py
│   ├── chromadb_policy_tool.py
│   └── northstar_audit_logger.py
├── tests/
├── README.md
├── requirements.txt
└── .env.example
```

## Team

- Precious Ajayi — Orchestrator Engineer
- Usen Usen — Prompt Engineer
- David Quezada — QA / Critic Engineer
- Christopher Boykin — Integration / Logging & Observability Engineer

## Development Workflow

Development uses feature branches and pull requests.

The `main` branch represents the shared, stable version of the project.