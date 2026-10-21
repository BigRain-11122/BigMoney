# E63 — the off-cycle penalty is not a fee: switch the cost off and the gap does not move

Cutoff 2026-10-20 · leg `midsweep --costs 0,3` in `scripts/e39_panel_census.py` (selftest 94/94)
Faces: `results/e44_midmonth/MIDSWEEP-20261020-c0_3.json` (start 2020),
`results/e44_midmonth/MIDSWEEP-20261020-s20130101-c0_3.json` (start 2013)

## Question

E59 showed every off-cycle decision date loses to month-end in the newest era with
turnover in the same 0.565–0.594 turns/yr band. Same turnover is an inference, not a
measurement. E63 measures it: burn the identical sweep with the engine's fee switched
off (x0) and again at three times the fee (x3). A gap that survives x0 is a price-path
effect — the book is struck on different sessions and holds different marks over the
same months. A gap that moves with the fee is the cost of trading on that date.

## Answer

**The gap is invariant to the fee.** Across five dates, both windows, full-window and
per-era: cost face shift is 0.0bp everywhere (era cells move by at most one rounding
unit, ±1bp).

| window | me ann x0 → x3 | full-window gap shifts (mid5/10/15/20/25) | newest-era gap x0 |
|---|---|---|---|
| start 2020 | +0.93% → +0.70% | 0.0 / 0.0 / 0.0 / 0.0 / 0.0 bp | −71 / −86 / −88 / −56 / −65 bp |
| start 2013 | +8.03% → +7.79% | 0.0 / 0.0 / 0.0 / 0.0 / 0.0 bp | −71 / −86 / −88 / −56 / −65 bp |

The fee itself is real and sized: x3 removes 22.1–23.2 bp/yr (start 2013) and
22.7–23.2 bp/yr (start 2020) — **a spread of 0.5bp/yr across six calendars**, against a
−70..−88bp calendar gap. Month-end pays 23.1bp/yr and mid-15 pays 23.2bp/yr on the same
window. The cost channel is therefore excluded directly, not by inference, and it is
excluded at both ends: at x0 nothing is paid and the gap is unchanged.

Two side readings:

- **x0 is the sanity check that the multiplier is live** — the x0 arms report
  `cost_per_year_bp = 0.0` for every book, so a flat cost face is a real switch-off, not
  a silently ignored argument.
- **The newest-era gap is bit-identical between the two windows at both cost levels**
  (−71/−86/−88/−56/−65), the same start-invariance E59 found at x1: that era's path does
  not depend on where the run begins. Everything older still does (pre2017 −125..+18bp,
  2021_2023 +36..−121bp), so older eras stay window-bound and must be quoted with their
  start date.

## What this rules out

The off-cycle penalty cannot be explained by trading more, trading a wider set, or
paying more per trade on a different day: it is a property of *when the book is struck
and what marks it then holds*, not of the friction of striking it. Any follow-up that
prices the calendar must therefore attack the path (entry timing / held marks), not the
fee line.

## Honest bounds

- Two cost levels (x0, x3), not a continuum; x1 is the E59 face already on record.
- Reported ann returns carry 0.01% = 1bp output resolution, so "0.0bp shift" means
  "below one instance of the printed precision"; the per-era ±1bp cells are exactly that
  rounding unit and are not read as real movement.
- Five fixed dates, no date searched for; no date here is a recommendation.
- Descriptive census only: no gate, no verdict, no prereg, zero trial count booked.
- The 2017_2020 column at start 2020 remains an exact 0.0bp cash block (E64's subject),
  unchanged by the cost switch — a cash-only slice has no fees to be sensitive to.

## Pool

E63 closed `done` with both faces as `result_ref`. Follow-up seeded:
**E65-MIDSWEEP-ENTRY-DELAY** — hold the month-end *names*, shift the *entry* by
1/3/5/10 sessions: if a delayed month-end book loses the same 60–90bp, the effect is
pure timing and membership is irrelevant. E64 (cash-share face) still waiting.