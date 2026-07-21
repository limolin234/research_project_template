---
name: deepseek-context-agent
description: Consult or extend a project-local DeepSeek context advisor that carries noisy ideas, attempts, cautions, and negative results in deepseek-context-agent/deepseek_context.md. Use when an agent needs cross-note synthesis, logical connections, or an explicitly typed working-context append without retaining query history.
---

# DeepSeek Context Agent

Use `scripts/context_agent.py` as the only interface. Use
`deepseek-context-agent/deepseek_context.md` for noisy working material that is
still useful for reasoning. The template tracks this file as an empty
placeholder; only `remember` writes records to it. Other project documents
remain outside this Skill's storage contract. Keep API credentials only in the
environment or ignored `.env`.

## Consult

Run from the target project directory so the fallback `.env` stays
project-local. The default context path is anchored inside the bundled Skill,
so changing the current working directory cannot move the default file.

```bash
python deepseek-context-agent/scripts/context_agent.py consult \
  "What assumptions currently limit this proposal?"
```

The command sends only the fixed system prompt, current working context, and
the current question. It never stores the question, DeepSeek reasoning, or the
returned answer. Use `--context PATH` for a non-default context file. The
context file must contain usable material before consultation.

Return only the command's formal JSON result to the main agent. Do not expose
or reconstruct chain-of-thought. Treat `sources`, credibility assessments,
conflicts, and uncertainties as part of the result rather than as hidden
reasoning.

## Remember

Read [references/write-format.md](references/write-format.md) before writing.
Append only when the user or main agent explicitly intends to retain working
context. Never turn a normal consultation into an automatic write.
`remember` writes only `deepseek-context-agent/deepseek_context.md` by default.
Do not edit the placeholder manually or use it as a separate project fact
ledger.

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
`DEEPSEEK_THINKING`, and `DEEPSEEK_CONTEXT_FILE`.

The template `.env.example` configures the same Skill-local file with the
relative path `deepseek-context-agent/deepseek_context.md`. Relative paths from
the environment are resolved from the fallback `.env` directory; an explicit
`--context PATH` is resolved from the current working directory. Keep the
default unless the project deliberately stores its working context elsewhere.

The default model is `deepseek-v4-flash`; thinking is enabled for synthesis,
but the wrapper discards `reasoning_content` and returns only allow-listed
formal fields. Use `--thinking disabled` only when lower latency matters more
than cross-record reasoning.

On Windows, use `py -3` with the bundled relative path or the resolved absolute
Windows path to the same script.
