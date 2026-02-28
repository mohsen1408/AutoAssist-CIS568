# Architecture

AutoAssist uses a multi‑agent workflow with validation and human‑in‑the‑loop checkpoints for safety‑critical steps.

## Agents
- **Questioner**: converts vague symptoms into a structured, vehicle‑aware problem statement
- **Researcher**: retrieves grounded repair notes and likely causes
- **Verifier**: checks fitment, safety, consistency; assigns confidence; triggers escalation
- **Planner**: converts verified notes into beginner‑friendly step‑by‑step instructions
- **Explainer**: translates technical details into plain language

## Guardrails
- Low confidence → ask clarifying questions
- Conflicting sources → re‑verify / escalate
- High‑risk repair → refuse + recommend professional service
