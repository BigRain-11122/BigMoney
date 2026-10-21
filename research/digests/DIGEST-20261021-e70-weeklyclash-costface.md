# E70 — the weekly book's gap is a price path, not a fee

> r1142 · bm-b · leg `weeklyclash` in `scripts/e39_panel_census.py` (selftest 107/107)
> faces: `results/e44_midmonth/WEEKLYCLASH-20261021-c0_3.json` (+ `-s20130101-c0_3`)
> descriptive census only — no gate, no verdict, no prereg, no trial count, zero ledger booking

## Question

E69 priced the month-end vs weekly clash at x1 only and **inferred** the fee channel from a
2.5 bp/yr parity (10.3 vs 7.8 bp/yr) against a −55 bp gap. Inference is not a burn. So: **switch the
cost multiplier off (x0) and back on hard (x3) and see which number moves** — if the weekly gap and
the retiming gap are unchanged at x0, both are price-path effects; if either moves with the fee, the
weekly grid's extra rebalances are paying for part of it.

One burn per window start, both cost levels inside the same face (`calendar_rows_by_cost`,
`cost_face`, `cost_shift_bp` — the two rows are read out of ONE face, not two burns).

## Answer

**The fee channel is closed outright, and it closes with the right magnitude.**

| window start | book | gap x0 | gap x3 | shift | fee x3 (bp/yr) | fee diff vs `me` |
|---|---|---|---|---|---|---|
| 2020-01-01 | `week` | −53.0 | −61.0 | **−8.0** | 30.9 | +7.8 |
| 2020-01-01 | `week_near_me` | −11.0 | −12.0 | **−1.0** | 23.3 | +0.2 |
| 2020-01-01 | `me` | 0 | 0 | 0 | 23.1 | — |
| 2013-01-01 | `week` | −5.0 | −14.0 | **−9.0** | 30.8 | +8.6 |
| 2013-01-01 | `week_near_me` | −15.0 | −15.0 | **0.0** | 22.4 | +0.2 |
| 2013-01-01 | `me` | 0 | 0 | 0 | 22.2 | — |

The shift of the weekly book (−8.0 / −9.0 bp) is the fee difference itself (7.8 / 8.6 bp/yr) within
rounding: switching the fee on moves the gap by exactly what the extra turnover costs. The residual
is the price path — −45 bp at the 2020 start, +4 bp at the 2013 start — and it does not respond to the
fee at all. The retiming book (`week_near_me`, which holds frequency at 1.008–1.005x month-end) is
**fee-neutral**: −1.0 bp shift at 2020, 0.0 bp at 2013, against a 0.2 bp/yr fee difference.

Turnover is identical between cost levels in every book (0.789 / 0.595 at 2020, 0.788 / 0.572 at
2013) and so is the turnover ratio to `me` (1.337 / 1.008 and 1.385 / 1.005), which is the control
that says the multiplier acts on fees only and not on the trading rule.

Absolute annualised levels move a lot with the fee (x0 → x3): `me` 0.93% → 0.70%, `week` 0.40% →
0.09%, `week_near_me` 0.82% → 0.58% at the 2020 start; `me` 8.03% → 7.79%, `week` 7.98% → 7.65%,
`week_near_me` 7.88% → 7.64% at 2013. The ordering of the three books is unchanged by the cost level,
so the E69 conclusion does not depend on the fee assumption.

## Honest limits

- Era-level shifts do not scale with the full-window fee difference (newest-era `week` shift −11 bp
  against a 7.8 bp/yr full-window fee gap), because an era is a subset of years and its fee load is
  not the full-window average. Era shifts are reported as they read, not as fee arithmetic.
- x0 is a frictionless counterfactual, not an achievable book; it exists to price the channel.
- Both starts are reported because full-window gaps are start-bound (E59/E63/E65–E69); only the
  newest-era column is bit-identical across starts.
- `week_near_me` is a snap (11/349 exact coincidences at 2020, 21/708 at 2013), so its residual is
  the price of being on the weekly grid, not a clean boundary reading.
- Descriptive census only: no gate, no verdict, no prereg, no trial count.

## Handoff

E71-WEEKLYCLASH-NAMES (seeded `waiting`, cpu-only): the −45 bp price-path residual of the full
weekly grid at the 2020 start is the last unexplained number in the calendar family. Census the held
names of `week` / `week_near_me` / `me` at the same decision dates (overlap share, entrant/exit
classification as in E57) — if the books hold the same names the residual is timing, if they diverge
it is membership. With that, the calendar family (E44/E59/E63/E65/E66/E67/E68/E69/E70) can be frozen
for a judged unit.