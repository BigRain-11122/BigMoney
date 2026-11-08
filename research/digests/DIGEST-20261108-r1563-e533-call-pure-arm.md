# DIGEST 2026-11-08 r1563 bm-b — E533: one call further is two different things

**Card**: E533 (pool) — for each open arm whose argument is a call, does that call fold to a literal
at its own site?
**Face**: `results/state_tilt/CALLPUREARM-2026-11-08.json` (+ `callpurearm_latest.json`)
**Tool**: `scripts/e533_call_pure_arm.py` (build / check / verify / selftest)
**Parent**: `results/state_tilt/UNDECIDABLEARM-2026-11-08.json` (E527)

## Headline

E527 left four arms open. Ask each one "is your argument a call, and does it fold?" and the answer
splits three ways, not two:

| arm | argument | kind | fold | outcome |
|---|---|---|---|---|
| `scripts/regime5_validation.py:577` | `list(range(6))` | direct call | **folds to `[0, 1, 2, 3, 4, 5]`** | **arm becomes decidable** |
| `scripts/e285_interrange_gap_ceiling.py:505` | `interval(off['rows'], 'tight', interval(...))` | direct call | callee is repo source (`e285…py:108`), not inlined | stays open |
| `scripts/regime5_validation.py:173` | `stats_idxs` | caller's own parameter | not a call | out of scope |
| `scripts/regime5_validation.py:319` | `win_stats` | name bound from a **list comprehension** over the panel | not a call | out of scope |

Verdict (re-derived by the gate): `a_one_call_fold_closes_some_of_the_call_argument_arms_but_not_all_of_them`.

## Two findings worth keeping

1. **"Still open" hides a scope problem.** Half of the four arms do not pass a call at all, so no
   amount of call-folding can ever settle them. The pool card's own seed text said `win_stats` was
   "bound from a call"; the source says
   `win_stats = [j for j in rb if dates[j] >= MAIN_START]` — a comprehension that reads the panel.
   A study that had followed the card instead of the source would have published a fold attempt
   against a value that never existed.
2. **"The callee is not a builtin this fold knows" is not the same as "the callee is opaque".**
   `interval` is defined at `scripts/e285_interrange_gap_ceiling.py:108`; the honest class is
   *repo source, not inlined here*. Its arguments also read `off['rows']`, so the arm has two
   independent reasons to stay open and both are now published.

## Method limits (published in the face)

- The fold is a strict whitelist (literals, containers of literals, arithmetic over those,
  subscripts of a folded container, builtin calls whose arguments all fold). A `Name`, an attribute,
  a comprehension or any other callee stops the fold and is published with the reason.
- A repo-source callee is not inlined, so "not a pure chain of literals" is a statement about this
  fold, not about the callee's purity. That is exactly what the seeded successor card (E536) is for.
- Arms E527 already settled are not re-opened; arms whose argument is not a call are published with
  their kind and counted as out of scope rather than dropped.
- Nothing is executed, no source is rewritten; `check` 0.05 s.

## Wiring

- S6 leg `call_pure_arm` (`Tools/s6_chain_bmb.py`) → rc0 0.05 s.
- Smoke leg appended to `smoke_test.py`; run standalone as `_r1563_leg533.py` → PASS, refuse checks
  green (hand-written verdict, closed arm with no folded value, folded value on a non-folding call,
  out-of-scope arm published as open).
- Methodology card E533 in `knowledge/METHODOLOGY_ASSETS.md` (append-only, numstat 10/0).