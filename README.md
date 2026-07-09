# Research Project Template

Minimal infrastructure for agent-assisted research projects.

The template starts small on purpose. It provides a stable place for human
judgment, agent expansion, project status, workflow rules, and research notes.
Add data, scripts, figures, claim ledgers, or graphs only when the project
actually needs them.

Important claims should have a visible verification path: source candidate,
research note, original-source reading, confidence level, and final prose
decision.

The files form a human-in-the-loop control loop: `manual.md` holds the human
line, `workflow.md` stores durable corrections, `AGENT.md` stores future
startup context, `docs_graph/` stores stage status and local project memory,
and `research_notes/` stores evidence state.

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
- `manual_agent.md`: AI-completed version of `manual.md`, for human review,
  selection, and possible merge-back.
- Do not co-author the same high-level file in parallel. Keep the human-owned
  line in `manual.md`; put agent completion in `manual_agent.md`.
- `workflow.md`: durable rules for human-agent collaboration.
- `AGENT.md`: project-level agent instruction/startup note, written by AI after
  the human states what the agent should remember. It is separate from the
  manuscript layer, so it does not conflict with `manual.md` or
  `manual_agent.md`.
- `docs_graph/`: self-contained project map, usage guide, and
  commit-to-commit status. It does not require an external docs-graph tool.
- `research_notes/`: sources, technical points, evidence notes, open questions,
  and negative results.

## Built-in Docs Graph

The `docs_graph/` folder is a small Markdown tree inside the project. It is
not a separate database and does not depend on a preinstalled skill. Use it as
path-addressable project memory:

- `docs_graph/docs_graph.md` explains how the local docs graph should be used.
- `docs_graph/status.md` records the current stage, last human decision,
  active task, evidence state, risks, next actions, and handoff notes.
- Add more files under `docs_graph/` only when a project area needs its own
  stable navigation or handoff note.
- Update `docs_graph/status.md` before stable commits and after major changes
  in direction.

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

Use this checklist when starting a new project from the template:

1. Create a new repository from the template, or copy the directory into a new
   project location.
2. Rename the project in this README and remove template-only wording that no
   longer applies.
3. Decide whether to keep the MIT license or replace it with the target
   project's license and copyright owner.
4. Set the Git remote to the new project repository, or remove the template
   remote before committing.
5. Reset `docs_graph/status.md` for the new project: fill the project name,
   stage, last human decision, active task, evidence state, risks, next
   actions, and handoff notes.
6. Fill `manual.md` with the human-owned project line: goal, audience, output,
   non-negotiable details, doubts, and stop conditions.
7. Ask the agent to complete `manual_agent.md` from `manual.md`. The agent may
   expand structure and checks, but should not overwrite `manual.md`.
8. Add real source candidates, technical points, open questions, and negative
   results to `research_notes/research_notes.md`. Do not keep placeholder rows
   as project evidence.
9. If the agent tool expects a different startup filename, add a short pointer
   file such as `AGENTS.md` or `CLAUDE.md` that tells it to read `AGENT.md` and
   `workflow.md`.
10. Make the first stable commit after `manual.md`, `manual_agent.md`,
    `docs_graph/status.md`, and `research_notes/research_notes.md` describe
    the new project rather than this template.

## Readiness

This template is usable as a lightweight starting point for research reports,
literature reviews, feasibility studies, and small experimental projects. The
main required discipline is initialization: do not treat template placeholders
or template status as project facts.

For larger projects, add claim ledgers, data folders, scripts, figures, or a
derived graph only after the default files are no longer enough.
