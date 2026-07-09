# Status

## Current State

- Minimal research project template is ready.
- Default structure is intentionally small: `workflow.md`, `manual.md`,
  `manual_agent.md`, `AGENT.md`, `docs_graph/`, and `research_notes/`.
- `manual.md` is human-owned. `manual_agent.md` is the AI-completed version of
  `manual.md`.
- Do not have humans and agents co-author the same high-level file in parallel;
  accepted agent output should be merged back deliberately.
- `research_notes/` is the default place for sources, technical points,
  evidence notes, open questions, and negative results.
- Source verification is part of the template workflow: important claims should
  record source candidates, original-source checks, confidence level, and final
  prose decision.
- Human feedback is modeled as a control loop: durable process corrections go
  to `workflow.md`, startup context goes to `AGENT.md`, phase handoff goes to
  `docs_graph/`, and evidence state goes to `research_notes/`.
- `data/`, `scripts/`, `figures/`, claim ledgers, and derived graphs are upgrade
  paths, not default folders.

## Next Steps

- Use this template to initialize downstream research projects.
- For each downstream project, fill `manual.md`, ask the agent to complete
  `manual_agent.md`, add initial research notes, and update this status file
  before the first stable commit.
