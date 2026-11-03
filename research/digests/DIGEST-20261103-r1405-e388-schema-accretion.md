# DIGEST r1405 / E388 -- is the trial-labor schema an accretion or a break?

**Study** `E388_schema_accretion_vs_break` · card `SCHEMAACCRETE-2026-11-03` · 2026-11-03 · bm-b
(CPU only, zero network, GPU parked per C-20261014-01, cloud untouched).

## The question

E386 published that the two merged basenames under `results/trial_labor_w*/` hold 31 distinct key
sets, and that zero in-repo readers read a basename bare. A shape count is not an answer: a reader
that names its wave still asks for *fields*. If the series only grows, every field an early reader
asks for is still there and the merge costs nothing. If a field stops being written, the reader gets
`None` (or `KeyError`, for a dict block) with no error and no version bump.

## The method

39 members (19 `judge_state.json`, 20 `prep_state.json`), compared **consecutive observed waves
only** — w15 and w20 hold no member, and treating a gap as a removal would manufacture two breaks
that never happened.

Four measurements per basename, none asserted:

* **walls** — fields added and removed between adjacent observed waves; a wall is a break iff it
  removes something, and every wall must satisfy `fields_to - fields_from == added - removed`;
* **runs** — each field's presence as maximal intervals, so a field that appears, disappears and
  comes back is not read as one long presence (`re_added` is a real column, measured 0 here);
* **value shape** — the JSON type of each field in every wave it appears in;
* **scalar fate** — for each numeric field dropped at a break, whether any quantity in the post-break
  schema carries the same value, *and* shares a name token with it.

The last clause is the study's own correction. Value equality alone "recovered" a dropped `d=4` by
matching an unrelated `a=4` in the next wave; a counterpart must share a name token, and value-only
matches are published separately as `value_coincidences` rather than folded into recovery.

## Readings

| | judge_state.json | prep_state.json |
|---|---|---|
| members | 19 | 20 |
| schema size, first → last | 8 → 12 | 7 → 6 |
| walls | 14 (12 accretion, 2 break) | 15 (14 accretion, 1 break) |
| break at | w16→w17, w19→w21 | w16→w17 |
| removed / added | 16/7, 1/1 | 18/0 |
| later waves on the wrong side | 3, 0 | 4 |

Family totals: **29 walls, 26 accretion and 3 break, 0 fields ever re-added, 0 type flips among
surviving names**. The series is a strict monotone chain from w1 to w16 — every wall there adds and
never removes — and then one wall changes the shape of the file: `blocks` (43 entries carrying
`n_surviving_arms`) and `judged_cells` (344) replace the per-factor `*_meta` dicts, and prep swaps
11 factor gates for 4 pipeline gates.

Scalar fate across the three break walls — 4 dropped numerics, 2 lost, 2 recovered:

| field | last value | recovered as |
|---|---|---|
| `n_survivors` (judge) | 40 | **nothing** — 43 blocks / 344 cells / cap 90 all differ |
| `n_distinct` (prep) | 173 | **nothing** |
| `n_starts_6m` (prep) | 1253 | `starts.len` = `passive_6m_ret.len` |
| `cap` (judge) | 90 | `cell_cap` |

One in-place vocabulary replacement: `gates` keeps its name while its contents become disjoint —
a reader keyed on `G-VOL` fails with `KeyError`, which is why the inner-vocabulary wall is published
apart from the top-level walls instead of being invisible in both.

## What this changes

E386's headline stands and sharpens: the merge costs the family a schema, and at a wall it also costs
it two numbers. "The merge loses a number" and "the merge loses a schema" stop being one flag: the
file's identity is continuous, the family's question is not, and the wrong side of the wall is named
per field (`waves_after_last_seen`), so a reader can be told which waves will answer `None`.

## Wiring

* `scripts/e388_schema_accretion.py` — `run` / `verify` (problems=[]) / `selftest` 33/33
* smoke leg E388 executed verbatim by `scripts/run_e388_smoke_leg.py` (1/1)
* S6 leg `schema_accretion` (rc 0, 0.95 s)
* `results/state_tilt/SCHEMAACCRETE-2026-11-03.json` + `schemaaccrete_latest.json`
* card `knowledge/METHODOLOGY_ASSETS.md` E388

## Next

E389 — what do the 18 family-glob readers actually compute? An aggregate that takes the latest member
by mtime answers a different question than a sum over members, and the family-wide sum of
`n_survivors` has no single value after w17 because the field moved shape.