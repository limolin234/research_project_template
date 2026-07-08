# Workflow

## Scope

This template configures a small, durable workspace for research projects with
agent assistance. The goal is not to predict every future folder, but to make
the project readable, recoverable, and easy for humans and agents to continue.

## Core Rules

- Keep the default structure small.
- `manual.md` is the human-owned project line. Do not replace it with an
  agent-generated outline.
- `manual_agent.md` is the agent expansion of `manual.md`. It may add tasks,
  missing structure, and suggested checks, but it remains review material.
- `workflow.md` stores durable rules. If feedback reveals a repeated mismatch,
  update this file.
- `AGENT.md` is a scratchpad for agent-local notes and startup guidance.
- `docs_graph/` stores project navigation and status, not long prose.
- `research_notes/` stores sources, technical points, open questions,
  evidence notes, and negative results.

## Context Rule

Only load context needed for the current task. Keep side questions, speculative
routes, and temporary doubts out of the main working context until they become
project knowledge.

Use forks or separate notes for exploratory discussions. Merge conclusions back
into `manual.md`, `workflow.md`, `docs_graph/`, or `research_notes/` only after
they become stable.

## Research Notes Rule

Start with `research_notes/research_notes.md`. Do not create a claim ledger,
data folder, or knowledge graph by default.

Upgrade only when needed:

- Split files when `research_notes.md` is too large to scan.
- Add `claim_ledger.csv` only when the report has many auditable factual,
  numerical, comparative, or causal claims.
- Add `data/`, `scripts/`, or `figures/` only when those artifacts exist.
- Add a generated graph only when relationships are too complex for notes and
  ledgers. The graph is a derived view, not the source of truth.

## Agent Work Rule

- Read `workflow.md`, `manual.md`, `manual_agent.md`, `docs_graph/status.md`,
  and `research_notes/research_notes.md` before substantial work.
- Preserve human judgment in `manual.md`.
- Put agent expansions in `manual_agent.md`.
- Keep process language out of final deliverables.
- Make outputs reproducible when scripts, data, or figures are involved.

## Commit Rule

Commit stable phases. A good commit keeps the human line, agent expansion,
research notes, docs graph, and generated outputs aligned.
