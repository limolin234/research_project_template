# Workflow

## Scope

This template configures a small, durable workspace for research projects with
agent assistance. The goal is not to predict every future folder, but to make
the project readable, recoverable, and easy for humans and agents to continue.

## Core Rules

- Keep the default structure small.
- `manual.md` is the human-owned project line. Do not replace it with an
  agent-generated outline.
- `manual_agent.md` is the AI-completed version of `manual.md`. It may fill
  gaps, expand structure, and suggest checks, but it remains review material
  until the human accepts or merges parts back.
- Do not have humans and agents co-author the same high-level file in
  parallel. Keep one owner per layer: humans own `manual.md`; agents complete
  `manual_agent.md`; accepted parts are merged back deliberately.
- `workflow.md` stores durable rules. If feedback reveals a repeated mismatch,
  update this file.
- `AGENT.md` is project-level agent instruction/startup context. In research
  projects, the human should state what the agent should remember, then the
  agent may write or update `AGENT.md`. This is separate from the manuscript
  layer, so it does not conflict with `manual.md` or `manual_agent.md`.
  Durable rules still belong in `workflow.md`.
- `docs_graph/` stores project navigation and status, not long prose. It is a
  self-contained Markdown docs graph; read `docs_graph/docs_graph.md` for its
  local usage rules. The agent should update it at stable phases.
- `research_notes/` stores sources, technical points, open questions,
  evidence notes, and negative results. The agent maintains it during execution;
  humans review critical claims and final conclusions.

## Human-Agent Role Rule

- Human-owned: problem direction, `manual.md`, critical judgment, evidence
  acceptance, stop conditions.
- Agent-owned: `manual_agent.md`, routine `docs_graph/` status updates,
  `research_notes/` maintenance, compilation, rendering, source collection,
  scripts, figures, and draft patches.
- Project-owned: the file layout, workflow rules, tools, git history, and
  reproducible artifacts that keep human and agent work separable.
- The agent may edit `workflow.md` and `AGENT.md` when the human asks it to
  record a stable project rule or startup instruction.

## Control Loop Rule

Treat the project as a human-in-the-loop control system:

- goal and judgment loop: `manual.md` and final human acceptance;
- rule loop: repeated corrections and durable standards go to `workflow.md`;
- startup-context loop: project-level reminders for future agent sessions go to
  `AGENT.md`;
- status loop: current state, next steps, and handoff notes go to
  `docs_graph/`;
- evidence loop: sources, claims, negative results, and verification states go
  to `research_notes/`.

The agent should update `docs_graph/` at stable phases. It should update
`workflow.md` or `AGENT.md` only when human feedback has become a durable rule
or startup requirement.

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

## Source Verification Rule

- Treat important factual, numerical, comparative, or causal statements as
  claims with verification states.
- Use search tools or paper-search skills to collect candidates, then record
  sources, negative results, and open questions in `research_notes/`.
- Prefer primary sources: full papers, standards, official specifications,
  source code, raw data, or reproducible project calculations.
- The main agent must read original sources before using critical claims in
  final prose. Subagents may audit missing routes or source boundaries.
- Grade source confidence before writing: primary/official, secondary clue,
  internal model, or unverified. Downgrade wording when verification is
  incomplete.
- Add a claim ledger only when sentence-level tracking becomes necessary.

## Agent Work Rule

- Read `workflow.md`, `manual.md`, `manual_agent.md`, `docs_graph/status.md`,
  and `research_notes/research_notes.md` before substantial work.
- Preserve human judgment in `manual.md`.
- Put AI completion of the human manual in `manual_agent.md`.
- Do not overwrite human-owned high-level files with agent-generated structure.
- Keep process language out of final deliverables.
- Make outputs reproducible when scripts, data, or figures are involved.

## Commit Rule

Commit stable phases. A good commit keeps the human line, agent expansion,
research notes, docs graph, and generated outputs aligned.
