# DIGEST — W22 pre-screen (pre-holiday multi-bar hold, placebo null)

**Face**: `scripts/w22_null_screen.py` (selftest 15/15) →
`results/trial_labor_w22/w22_cheap_screen.json`
**Grammar**: `results/trial_labor_w22/w22_grammar.json` sha16 `ac29b0715bcbbe06`
(10 cells = {hol_pre1, hol_pre2} × h{1..5}, K=200, seed 20670000, HEAVY face
untouched — this is the cheap screen the labour law asks for before a burn)
**Face data**: E23 daily equal-weight panel face, cutoff 2026-10-19
**Runtime**: 3.0 s, zero network, zero engine/prereg/judged/pool write

## Reading (excess over the day-pool baseline, one observation per day)

| cell | excess | n | two-sided p | z vs placebo |
|---|---|---|---|---|
| hol_pre1@h4 | **+103.4 bp** | 180 | **0.0100** | 2.82 |
| hol_pre1@h3 | +69.5 bp | 180 | 0.0299 | 2.21 |
| hol_pre1@h2 | +54.3 bp | 180 | 0.0398 | 2.05 |
| hol_pre1@h5 | +75.6 bp | 180 | 0.0597 | 1.73 |
| hol_pre2@h5 | +81.6 bp | 180 | 0.0746 | 1.88 |
| hol_pre1@h1 | +26.5 bp | 180 | 0.1045 | 1.53 |
| hol_pre2@h1 | −23.1 bp | 181 | 0.1841 | −1.31 |
| hol_pre2@h4 | +47.8 bp | 180 | 0.1891 | 1.32 |
| hol_pre2@h3 | +32.3 bp | 180 | 0.3632 | 0.97 |
| hol_pre2@h2 | +3.7 bp | 180 | 0.9154 | 0.13 |

**Family face** (max |excess| over the 10 cells vs the placebo family-max null):
observed 103.4 bp, **p_family = 0.0398** (K=200 ⇒ floor 0.00498).
**Holm step-down**: **zero survivors** — the top rank needs p ≤ 0.005 and the
best cell sits at 0.0100.

## Decision

`SCREEN_ZERO_SURVIVOR`. The pre-holiday family shows a family-level footprint
(p≈0.04) concentrated in **hol_pre1 with h ≥ 2**, but **no single cell clears
multiplicity** at this resolution. Two consequences, both recorded as honest:

1. **Do not burn the 10-cell runner as drafted.** A 10-cell grid buys a
   multiplicity bar the best cell cannot clear; burning it would only re-derive
   the E23 census at higher cost.
2. **The only defensible continuation is a narrowed confirmation**: family =
   `hol_pre1`, h ∈ {3,4} (2 cells ⇒ Holm bar 0.025, and hol_pre1@h4 p=0.0100
   clears it). This narrowing is **post-hoc** (h=4 was already the census's
   post-hoc best), so it must be run as a **fresh-window confirmation**, not as
   a discovery claim — pre-register it with the exit axis already frozen
   (`strategy_own`, exact-h-bar close, engine default stack disabled) and
   report it as confirmation-only.

## Caveats (carried verbatim in the JSON `honest` field)

- The placebo conditions only on window **count**, not on calendar structure.
- h>1 windows overlap; the placebo inherits the same overlap (like-for-like,
  but per-cell p values are not independent draws).
- K=200 caps the family resolution at 1/201; more K is a compute decision, not
  a science-degree-of-freedom decision.
- No cost model here — cost stays with the E23 cost face and the runner exit
  axis (E23: pre-holiday switch ≈1.32 %/yr, net ≈0 at h=1).

## Consumers

- `research/TRIAL_LABOR_W22_PREREG.md` — sec. 5 supply decision (narrow or axe).
- Supply floor (ready units): none added this round; the screen is the input
  that decides which unit, if any, is worth feeding.