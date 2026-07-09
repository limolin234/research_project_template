# Docs Graph

Project-local navigation and memory for humans and agents.

This directory is self-contained. It does not require an external docs-graph
skill, graph database, vector database, or separate repository. The filesystem
tree is the graph: directories define project areas, and Markdown files hold
concise notes that can be read selectively.

## Core Idea

- Keep stable project context inside the repository.
- Use paths as addresses, for example `docs_graph/status.md`.
- Keep notes concise enough that a human or agent can quickly reload the
  project state.
- Let Git version, diff, branch, and roll back these notes together with the
  project.
- Keep transient reasoning out unless it has become durable project knowledge.

## Core Files

- `workflow.md`: durable collaboration rules.
- `manual.md`: human-owned project line.
- `manual_agent.md`: AI-completed version of `manual.md`.
- `research_notes/research_notes.md`: sources, technical points, evidence
  notes, open questions, and negative results.
- `docs_graph/status.md`: current status, active task, evidence state, risks,
  next actions, and handoff notes.

## How To Update

1. Read `workflow.md`, `manual.md`, `manual_agent.md`,
   `docs_graph/status.md`, and `research_notes/research_notes.md` before
   substantial work.
2. Update `docs_graph/status.md` after stable changes in project direction,
   evidence state, output state, or next actions.
3. Keep status entries factual and short. Put long evidence details in
   `research_notes/`, not here.
4. When a project area needs repeated handoff or navigation, create a
   subfolder and a same-name entry file, for example
   `docs_graph/modeling/modeling.md`.
5. Add cross-links by file path, not by copying large blocks of text.
6. Commit docs graph updates together with related research notes, scripts,
   figures, or draft changes when practical.

## Expansion Rule

Start with this file and `status.md`. Add more docs graph files only when one
file becomes too large to scan or when a project area needs its own stable
navigation.
