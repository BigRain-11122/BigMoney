# r1321 (bm-b) -- E292: the "move the count" fix plan, priced (and mostly refused)

**Face:** `results/state_tilt/BANDSCOPEFIX-2026-10-29.json` (+ `bandscopefix_latest.json`)
**Runner:** `scripts/e292_scope_fix_plan.py` -- `verify` 0 problems, `selftest` 16/16
**Card:** `knowledge/METHODOLOGY_ASSETS.md` E299 · **Chain leg:** `scope_fix_plan` (0.28s) · **Smoke leg:** E292

## What was inherited

E290 profiled the 27 self-auditable counts and then handed the un-derivable half on as work: 301 rows
over 299 scopes "whose face already publishes the unit the count's name claims", with the instruction
"move the count, no new data needed". That is a plan, so it can be priced.

## What the price is

| shape | rows | what it means |
|---|---|---|
| `needs_own_records` | 24 | the key IS the unit -- no sibling list of that name can ever exist in the same parent |
| `choice_required` | 76 | the unit is published as a list in more than one scope: the author must pick the collection |
| single target | 201 | exactly one list of that unit exists somewhere in the face |
| · agree with it | 126 | -- every one of them **foreign scope + list of at most one item** |
| · disagree with it | 75 | the move would immediately publish a new disagreement |

**Zero of the 201 single-target rows land beside a list in their own scope or in a scope that contains
or sits under it.** The 126 agreements live in unrelated subtrees (`sweep.count_fields_not_assessed
.by_key[i].n_faces` against `sweep.label_universe.faces`, a list of one label), and 126 of 126 of those
target lists hold at most one item -- a one-element list agrees with any count that happens to be 1.

Verdict: `the_elsewhere_scope_premise_does_not_hold_no_move_lands_in_a_scope_related_to_the_count`.

## Disclosure of the vocabulary amendment

The first build scored agreement without asking where the candidate list lives: 126 clean / 75 convict.
Adding the scope relation showed both numbers were about foreign subtrees and that no row lands in a
related scope at all -- a state the four declared verdicts could not express. V4 was declared for it and
the first counts are kept verbatim in `frozen_spec.vocab_amendment` rather than dropped.

## What this changes downstream

- The 301 rows no longer count as "cheap naming fixes" in any backlog arithmetic: they need their own
  records (24) or a scope decision (76) or they measure a collection the face never enumerates (201).
- Any future "move the count" proposal must publish the scope relation and the degenerate-target share
  beside the agreement, or it re-sells coincidence as auditability.

## Pit notes

1. Agreement is necessary, not sufficient: price the candidate by where it lives.
2. A bare unit name can never be relocated.
3. Pool writer pit (r1318) re-checked: patch applied with `newline='\r\n'`, line delta 25542 -> 25545.