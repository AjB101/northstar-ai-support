# Northstar AI Support

A multi-agent AI customer support ticket triage system developed for TEPP Phase 2.

## Business Problem

Northstar Support Co. currently relies on human support agents to manually classify incoming customer tickets, locate relevant company policies, draft responses, and submit responses for supervisor review.

Our goal is to explore how a multi-agent AI system can improve the speed and scalability of this workflow while preserving human oversight.

## Proposed Architecture

Our initial architecture includes:

- Triage Agent
- Policy retrieval using ChromaDB
- Response Agent
- Critic Agent
- Python-based orchestration and routing
- Retry logic
- Human approval
- Logging and observability

## Team

- Precious Ajayi — Orchestrator Engineer
- Usen Usen — Prompt Engineer
- David Quezada — QA / Critic Engineer
- Christopher Boykin — Integration / Logging & Observability Engineer

## Communication

Slack: `northstar-ai-lab`

## Development Workflow

Development will use feature branches and pull requests.

The `main` branch represents the shared, stable version of the project.
