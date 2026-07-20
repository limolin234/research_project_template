# DeepSeek Context Agent

`deepseek-context-agent` is a small, cross-platform context advisor for a main
agent. It keeps noisy working material in an append-only
`deepseek_context.md`, and asks DeepSeek to synthesize it for each question.

The primary deployment is project-level: bundle the generic Skill with the
project and version `deepseek_context.md` with the rest of the project. Other
project memory files remain outside this Skill's storage contract. The Skill
contains no project-specific knowledge itself.

It is intentionally not a vector database or graph store. It is for hypotheses,
ideas, attempts, cautions, negative results, and unfinished reasoning that are
useful across tasks.

## Requirements

- Python 3.10 or newer
- A DeepSeek API key with access to the configured model
- Network access to the configured API endpoint

The implementation uses only the Python standard library. No package install is
required.

## Installation

When the complete `deepseek-context-agent/` directory is bundled in a project
root, no installation is required. Run its script from that project root:

```bash
python deepseek-context-agent/scripts/context_agent.py types
```

On Windows, use the Python launcher when needed:

```powershell
py -3 .\deepseek-context-agent\scripts\context_agent.py types
```

For user-level reuse, install the complete directory under the Codex skills
directory and restart the Codex session:

- POSIX default: `${CODEX_HOME:-$HOME/.codex}/skills/deepseek-context-agent`
- Windows default: `%CODEX_HOME%\skills\deepseek-context-agent`, or
  `%USERPROFILE%\.codex\skills\deepseek-context-agent` when `CODEX_HOME` is not
  set

The skill wrapper and CLI use the same script. Installing the skill does not
create a context file; the first explicit `remember` call creates the
configured file in the working project.

## Configuration

The process environment takes precedence. If a value is missing or blank, the
tool loads only these keys from `./.env`:

```dotenv
DEEPSEEK_API_KEY=your-key
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_THINKING=enabled
DEEPSEEK_CONTEXT_FILE=deepseek_context.md
```

The `.env` file is optional and should not be committed. Other variables in the
file are ignored so a project context file cannot change proxy or unrelated
network configuration. Pass `--env-file PATH` when the fallback file is stored
elsewhere.

## Usage

Run from the project directory. On Windows, use `py -3` instead of `python` if
the `python` command is not registered.

Create one typed working-context record:

```bash
python deepseek-context-agent/scripts/context_agent.py remember \
  --type hypothesis \
  --basis inference \
  --source "user discussion" \
  "Full-context synthesis may be more useful than fragment retrieval here."
```

Ask the context advisor:

```bash
python deepseek-context-agent/scripts/context_agent.py consult \
  "Which assumptions currently limit this proposal?"
```

The default record file is `./deepseek_context.md`. Override it with
`--context PATH` or `DEEPSEEK_CONTEXT_FILE`. Consultation requires useful
content in the context file.

Inspect the conservative local budget estimate without making an API call:

```bash
python deepseek-context-agent/scripts/context_agent.py budget \
  "What is relevant to this design decision?"
```

## Consultation behavior

Each consultation constructs a fresh request containing:

```text
fixed system prompt + current deepseek_context.md + current question
```

The question, returned answer, and DeepSeek `reasoning_content` are never
written to the context file or reused in the next request. Every query is a
fresh branch from the same context snapshot. The wrapper returns only these
formal fields:

- `content`
- `supporting_information`
- `logical_connections`
- `conflicts`
- `uncertainties`

The wrapper discards unapproved fields, including nested analysis or reasoning
fields. The system prompt asks DeepSeek to distinguish source-backed material,
user decisions, inference, speculation, and unknowns, and to report dynamic
support, conflict, dependency, limitation, and extension relationships.

## Write boundary

`remember` is the tool's only write operation. It writes only
`deepseek_context.md`, appends one Markdown record, and does not create IDs,
graph edges, query logs, or automatic model writes. The allowed types are:

```text
source-note, decision, hypothesis, insight,
caution, negative-result, open-question
```

Every record requires a `basis`, one or more `source` values, and content. The
type/basis combinations are defined in
[`references/write-format.md`](references/write-format.md). A normal
consultation never promotes its own output into memory.

`deepseek_context.md` is project content, not a cache. Keep it under the
project's normal version control unless that project's policy explicitly says
otherwise. Other project memory files are outside this Skill's contract.

## Context limits and errors

The default model is `deepseek-v4-flash`, whose advertised context length is
1M tokens. The tool uses a conservative character-class estimate with higher
weights for punctuation, CJK text, and other Unicode, plus a safety margin and
the reserved output budget:

- at or above 600,000 estimated tokens: write a warning to stderr and continue;
- above 900,000 estimated tokens: reject the request before network access;
- below the warning threshold: continue normally.

The estimate is not a replacement for the model tokenizer. It is an early
guard against accidentally filling the entire context window. Cache hits reduce
input cost but do not increase the context limit or guarantee retrieval quality.

No usable project memory, invalid file paths or `.env` lines, invalid write
types, permission errors, timeouts, HTTP failures, invalid API JSON, malformed
formal output, and budget violations are reported as a JSON error on stderr
with exit code `2`.
