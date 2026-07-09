# Agent Startup Context

This file is project-level agent startup context. It is not part of the
manuscript layer.

For research projects, the human and the agent may repeatedly discuss and
change goals, structure, and output style. The human should state what the
agent should remember at the project level; the agent may then write or update
this file as startup context.

Durable project rules belong in `workflow.md`; project status belongs in
`docs_graph/status.md`.

Recommended startup:

1. Read `workflow.md`.
2. Read `manual.md` and `manual_agent.md`.
3. Read `docs_graph/docs_graph.md` and `docs_graph/status.md`.
4. Read `research_notes/research_notes.md`.
5. Keep `manual.md` human-owned. Put AI completion in `manual_agent.md`.

First-run guard:

- If `manual.md`, `manual_agent.md`, `docs_graph/status.md`, or
  `research_notes/research_notes.md` still contain only template placeholders,
  do not treat them as project facts.
- Follow the `First Use` checklist in `README.md` before substantial work.
- If the project goal, license, remote, or output target is unclear, ask for
  that missing setup information instead of inventing it.
