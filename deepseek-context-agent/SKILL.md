---
name: deepseek-context-agent
description: Consult or extend a project-local DeepSeek context advisor that reads source-traceable facts from fact.md and carries noisy ideas, attempts, cautions, and negative results in deepseek_context.md. Use when an agent needs cross-note synthesis, source-aware credibility assessment, logical connections, or an explicitly typed working-context append without retaining query history.
---

# DeepSeek Context Agent

Use `scripts/context_agent.py` as the only interface. Maintain source-traceable,
verified facts in project-root `fact.md`. Use `deepseek_context.md` only for
noisy working material that is still useful for reasoning.
Treat both Markdown files as project-owned artifacts that can travel with the
project's normal version history. Keep API credentials only in the environment
or ignored `.env`.

## Consult

Run from the target project directory so default project files and `.env` stay
project-local. When the Skill is bundled in the project root, use the relative
path shown below. For a user-level installation, replace
`deepseek-context-agent` with the resolved absolute Skill directory.

```bash
python deepseek-context-agent/scripts/context_agent.py consult \
  "What assumptions currently limit this proposal?"
```

The command sends only the fixed system prompt, current `fact.md`, current
working context, and the current question. It never stores the question,
DeepSeek reasoning, or the returned answer. Use `--fact PATH` or `--context
PATH` for non-default files. Either project file may be absent or empty, but at
least one must contain usable material.

Return only the command's formal JSON result to the main agent. Do not expose
or reconstruct chain-of-thought. Treat `sources`, credibility assessments,
conflicts, and uncertainties as part of the result rather than as hidden
reasoning.

## Remember

Read [references/write-format.md](references/write-format.md) before writing.
Append only when the user or main agent explicitly intends to retain working
context. Never turn a normal consultation into an automatic write.
`remember` writes only `deepseek_context.md`; update `fact.md` directly after
verifying a fact and its source.

```bash
python deepseek-context-agent/scripts/context_agent.py remember \
  --type hypothesis \
  --basis inference \
  --source "user discussion" \
  "Full-context reasoning may be more useful than fragment retrieval here."
```

The command validates the type/basis combination and appends one record. It
does not create IDs, graph edges, query logs, or model-generated relations.

Before a large consultation, estimate the request without making an API call:

```bash
python deepseek-context-agent/scripts/context_agent.py budget \
  "What is relevant to this design decision?"
```

The guard warns at an estimated 600,000 tokens and rejects above 900,000,
leaving room below the model's advertised 1M-token context limit.

## Configuration

Read `DEEPSEEK_API_KEY` from the process environment first. If it is missing,
load `./.env` without overriding existing environment variables. Optional
variables are `DEEPSEEK_MODEL`, `DEEPSEEK_BASE_URL`,
`DEEPSEEK_THINKING`, `DEEPSEEK_FACT_FILE`, and `DEEPSEEK_CONTEXT_FILE`.

The default model is `deepseek-v4-flash`; thinking is enabled for synthesis,
but the wrapper discards `reasoning_content` and returns only allow-listed
formal fields. Use `--thinking disabled` only when lower latency matters more
than cross-record reasoning.

On Windows, use `py -3` with the bundled relative path or the resolved absolute
Windows path to the same script.
