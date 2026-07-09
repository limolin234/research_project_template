# Research Notes

Lightweight home for sources, technical points, evidence notes, open questions,
and negative results.

Start with one file. Split only when this becomes hard to scan.

## Source Registry

| id | title | type | link_or_doi | date_or_version | used_for | status | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

Use statuses such as `candidate`, `read`, `verified`, `rejected`, `negative`,
and `pending`. Add rows only for real sources; do not keep placeholder rows as
project evidence.

## Technical Points

- TBD

## Evidence Notes

- TBD

## Source Credibility Levels

| level | source type | allowed use |
| --- | --- | --- |
| A | full paper, standard, official specification, source code, raw data | supports technical claims with stated conditions |
| B | review, author slide, company release, course note | background or route clue; key numbers need A-level confirmation |
| C | internal model, script, manual estimate | model result or estimate with assumptions |
| D | AI output, unverified draft, web summary, second-hand quote | pending item only |

## Claim Handling

For important claims, record:

- source id
- claim text
- checked condition, unit, date, and version
- confidence level
- final prose decision: confirmed, downgraded, pending, or omitted

## Open Questions

- TBD

## Negative Results

Record failed searches, rejected sources, and routes that should not be
repeated.

- TBD

## Upgrade Triggers

- Add `claim_ledger.csv` only when many claims need sentence-level traceability.
- Add `data/`, `scripts/`, or `figures/` only when real artifacts exist.
- Add a generated graph only when relationships are too complex for notes and
  ledgers.
