# DIGEST r1403 — E387: republish the faces that no longer re-derive

**Round**: 1403 (bm-b) | **Dept**: research + engineering | **Lane**: cpu-only, static, zero network
**Face**: `results/state_tilt/REPUBLISH-2026-11-03.json` (+ `republish_latest.json`)
**Script**: `scripts/e387_republish_audit.py` (selftest 11/11, verify problems=[])

## What the suite said when this round opened

`python -m smoke_test` in-window: **280/285 PASS, 5 FAIL** (the 08:59 run was 277/7; the extra red
was that round's own heartbeat artifact, already fixed). Four distinct faces behind five legs:

| face | leg's own words |
|---|---|
| `precisiongap_latest.json` | the priced rows do not re-derive |
| `siblingentry_latest.json` | the face names no corpus, so its population cannot be rechecked |
| `UNSTAMPEDCENSUS-2026-11-02.json` | `siblingentry_latest.json` names no pin that is on disk |
| `unreadstatus_latest.json` | the published summary does not re-derive |

Two of these are the same defect counted twice (the E364 inventory reads the E335 face), and one is
the E346 face read a second time through its runner head.

## The three columns

A red that compares a published face against a fresh build has two causes the leg cannot separate:
the corpus moved (republish) or the face was never reproducible (seam, E368). The audit publishes
all three address columns so the decision is arithmetic rather than an opinion.

| face | moved since HEAD | replay from its pin | verdict |
|---|---|---|---|
| precisiongap | yes (rows) | no pin declared | republished |
| siblingentry | yes (corpus grew 2381 → 2415) | pin now on disk, **digests only** | seam |
| UNSTAMPEDCENSUS | no | — | parked (its red was the E335 pin) |
| unreadstatus | yes (summary) | no pin declared | republished |

## The repair that mattered

`siblingentry_latest.json` already carried a `corpus` stamp: `pin_id` over members, and a member
count equal to its own `sources_read` (2408 = 2408). It had no `corpus_source.pin_file`, so E363's
inventory called it STAMPED and then found no pin on disk. The fix lives in the builder, not the
leg: `scripts/e335_sibling_entry_point.py` now writes the pin from the same file list the numbers
were computed over (`CORPUSPIN-SIBLINGENTRY-2026-11-01.json`) and the face references it. No
assertion moved — `frozen_legs_edited: 0` is published and asserted.

## Pit that cost the most wall time

**A census over the live tree is self-perturbing.** The study's own new scripts join the corpus it
counts, so a `pin_id` taken before the last script was written can never match the corpus after it.
The first E387 leg went red on `corpus_source.pin_id` — no reader-visible number — purely because
two scripts were added between the pin write and the audit. The fan-out must be rebuilt on the
settled tree (pin owner → inventory → audit) and only then compared.

Second pit: the leg was inserted into `smoke_test.py` with 4-space indentation inside a module-level
block; the suite died at import with IndentationError and produced zero output. Caught by reading
stderr of the detached run rather than assuming the silence was a slow leg.

## Boundary

- `UNSTAMPEDCENSUS-2026-11-02.json` is rebuilt in place: the study keeps one frozen face name by
  design, so its date is not a wall-clock vintage.
- Replay is unavailable for every one of these faces because the pins store digests, not bytes —
  E372's 128-member gap. `seam` is therefore the honest verdict, not `republished`.
- The full suite was re-run after these repairs; the verdict is recorded in the round report.