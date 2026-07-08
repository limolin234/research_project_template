# Research Project Template

Minimal infrastructure for agent-assisted research projects.

The template starts small on purpose. It provides a stable place for human
judgment, agent expansion, project status, workflow rules, and research notes.
Add data, scripts, figures, claim ledgers, or graphs only when the project
actually needs them.

## Structure

```text
.
├── AGENT.md
├── README.md
├── workflow.md
├── manual.md
├── manual_agent.md
├── docs_graph/
│   ├── docs_graph.md
│   └── status.md
└── research_notes/
    └── research_notes.md
```

## Roles

- `manual.md`: human-maintained project line, judgment, doubts, and stop
  conditions.
- `manual_agent.md`: agent-expanded version of the human line, for review and
  execution.
- `workflow.md`: durable rules for human-agent collaboration.
- `AGENT.md`: agent scratchpad and startup note. Durable rules do not belong
  here.
- `docs_graph/`: concise project map and commit-to-commit status.
- `research_notes/`: sources, technical points, evidence notes, open questions,
  and negative results.

## Upgrade Path

Keep the default tree lightweight. Add folders only when they have work to do:

- Add `data/` when the project has datasets or generated tables.
- Add `scripts/` when commands need to be reproducible.
- Add `figures/` when generated figures need provenance.
- Split `research_notes/` into multiple files when one file becomes hard to
  scan.
- Add a claim ledger when the project contains many auditable factual or
  causal claims.
- Generate a graph only as a derived view from notes or ledgers, not as the
  default source of truth.

## First Use

1. Rename the project in this README.
2. Fill `manual.md` with the human-owned project line.
3. Ask the agent to expand `manual_agent.md`.
4. Add initial sources, technical points, and open questions to
   `research_notes/research_notes.md`.
5. Update `docs_graph/status.md` before each stable commit.
