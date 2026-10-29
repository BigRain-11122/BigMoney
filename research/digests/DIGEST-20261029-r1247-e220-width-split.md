# E220 — the width ladder's movement is the calendar part, and that part is not width-pure either

Round: r1247 (bm-b) · cutoff 2026-10-28 · face `results/e44_midmonth/WIDTHSPLIT-20261028.json`
· runner `scripts/e39_panel_census.py sharedbookwidthsplit` · card E220

## What was open

E219 established that the mid-month calendar gap is **not** width-invariant: +18 / −50 / −161 /
−45 bp at `pick_n` 10 / 25 / 50 / 100, spread 179bp against a 43.5bp tightest standard error. That
closed the "is this one effect measured more finely?" question with a no, and left a mechanism
question open:

- **Reading A (composition)** — wider rungs offer a different candidate set, so the rungs are
  measuring different portfolios. The gap would be an artifact of what is on offer.
- **Reading B (calendar)** — the same calendar offset is applied to a different book, so its value
  depends on the portfolio. The gap is real but not transferable across widths.

These imply opposite next steps, and the E61 identity `total = timing + selection` decides between
them at zero cost: the ladder already publishes both parts at every rung.

## What was measured

| pick_n | total | selection | timing (= total − selection) | matched sd | SE |
|---|---|---|---|---|---|
| 10 | +18.0 | −66.0 | **+84.0** | 528.9 | 236.5 |
| 25 | −50.0 | +33.0 | **−83.0** | 237.3 | 106.1 |
| 50 | −161.0 | +27.0 | **−188.0** | 124.8 | 55.8 |
| 100 | −45.0 | −42.0 | **−3.0** | 97.3 | 43.5 |

- timing range **272.0bp**, selection range **99.0bp**
- steps: timing moves with the total in **3/3**, selection opposes it in **2/3**
- identity flag true at every rung (`identity_ok`), 0 broken rungs

Verdict label: `timing_carries_movement_without_a_width_invariant_number`.

## What it changes

The prior hypothesis — the movement is a selection/composition effect — is wrong. Selection is the
**bounded** part (−66..+33bp) and it partly offsets the total; timing is the part that swings.
So the ladder is not four views of the same calendar effect measured on different populations; it
is the calendar offset priced against four different books, and the price is unstable.

Consequently the mid-month calendar line closes: **there is no quotable calendar number at any
width**. E61 (split exists) → E218 (unresolvable at width 10) → E219 (four numbers, not one) →
E220 (the movement is timing, and timing is not width-pure) leaves the effect readable per width
only, with no single number to carry forward.

## Honesty notes

- timing is **derived by subtraction** from the published total and selection; it inherits that
  selection term's error and is not an independent burn. Rungs whose identity check fails would be
  listed in `identity_broken_widths` rather than trusted; there were none.
- cost ×0 on both arms, so all four numbers are gross of fees.
- the label reports which part **carries** the movement; it does not claim the timing part is
  exploitable, and a width-invariant timing part would still need a cost arm before any such
  reading.
- descriptive census only: no gate, no prereg, no trial count.

## Pieces shipped

- `scripts/e39_panel_census.py` mode `sharedbookwidthsplit` + `_widthsplit_rows` /
  `_widthsplit_range` / `_widthsplit_movement` / `_widthsplit_verdict` + `WIDTHSPLIT_TOL_BP`
- `results/e44_midmonth/WIDTHSPLIT-20261028.json`
- `Tools/s6_chain_bmb.py` leg immediately after `sharedbookwidthladder` (arithmetic only, so it
  re-derives every round instead of caching to a cutoff)
- `smoke_test.py` leg: face present, study name, chain position after the ladder, and every rung
  carrying both parts
- `knowledge/METHODOLOGY_ASSETS.md` card E220
- selftest 803 → **812** (9 legs)