# Write Format

`remember` appends one working-context record. It never creates an ID or a
relationship edge.

## Required fields

- `type`: the role of the record in later synthesis.
- `basis`: why the record should receive any credibility.
- `source`: one or more origins. Use a file path, DOI/URL, experiment name,
  `user discussion`, `agent inference`, or `unknown` rather than inventing a
  citation.
- `content`: concise working material worth carrying across tasks.

`scope` is optional and states where the content applies.

## Allowed types and bases

| Type | Purpose | Allowed basis |
| --- | --- | --- |
| `source-note` | Information extracted from a source or observation | `direct`, `source-backed` |
| `decision` | Accepted project direction | `direct`, `user-confirmed` |
| `hypothesis` | Unverified explanation or prediction | `inference`, `speculative`, `unknown` |
| `insight` | Synthesis across existing material | `source-backed`, `inference` |
| `caution` | Risk, limitation, or evidence boundary | `direct`, `source-backed`, `inference` |
| `negative-result` | Failed, rejected, or non-working route | `direct`, `source-backed`, `user-confirmed` |
| `open-question` | Unresolved issue worth carrying forward | `inference`, `unknown` |

Do not use `decision` for a model preference that no human accepted. Do not use
`source-note` for an unsupported inference. Verified, source-traceable facts
belong in project-root `fact.md`, not in this working context. A `source-note`
is only a preliminary extraction retained for later synthesis.

## Stored representation

The script writes a model-readable Markdown block:

```markdown
---
type: hypothesis
basis: inference
source:
  - "user discussion"
scope: "DeepSeek context prototype"
content: |
  Full-context synthesis may be more useful than fragment retrieval for this
  small, noisy working set.
```

Records are append-only in v1. Query text and query results are never records.
