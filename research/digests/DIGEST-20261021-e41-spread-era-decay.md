# DIGEST 2026-10-21 — E41 spread by era: positive in all four, but the newest era is a quarter of the peak

Round r1116, bm-b. Script `scripts/e39_panel_census.py` (`era` leg, selftest 29/29).
Face `results/e41_spread_era/ERA-20261020.json`. Evidence cutoff 2026-10-20, full panel calendar
(2012-05-29 .. 2026-10-20), top9999 wide book, sh511 excluded, cost x1, 1,265 members.

## The question

The 2020+ pair leg found the spread curve carries its own −13.04% drawdown, so a single
full-sample number cannot describe it. This leg partitions the same ladder/wide/ratio curves into
four calendar eras and profiles each slice on its own (each re-based at its first bar).

## Measured

| era | bars | ladder5 | wide top9999 | vs-ladder | ladder maxDD | wide maxDD | ratio win rate |
|---|---|---|---|---|---|---|---|
| pre-2017 | 1,120 | +10.31 %/yr | +12.67 %/yr | **+236.0 bp** | −45.20% | −40.27% | 69.1% |
| 2017–2020 | 974 | +8.49 %/yr | +12.68 %/yr | **+419.0 bp** | −32.79% | −26.08% | 70.2% |
| 2021–2023 | 727 | −10.81 %/yr | −8.38 %/yr | **+243.0 bp** | −34.30% | −28.75% | 54.3% |
| 2024–now | 675 | +11.08 %/yr | +11.97 %/yr | **+89.0 bp** | −22.69% | −17.32% | 57.6% |

Spread is positive in **4 of 4** eras; the range across eras is 330bp (89 → 419).

## Why it matters

1. **The direction is not a regime.** Four independent calendar partitions, four positive spreads.
   The wide-book-over-ladder claim survives the era split, which is a stronger statement than the
   single 2020+ figure.
2. **The magnitude is.** Peak 2017–2020 (+419bp) versus newest era (+89bp) is a 4.7x compression.
   Anyone quoting "+134bp/yr" is quoting a mid-cycle number; the live era is below it and the
   boom era well above it.
3. **The newest era carries the worst ratio drawdown** (−13.04%, the same span the pair leg found:
   2025-07-24 → 2026-06-30). The weakest spread and the deepest spread drawdown are the same era —
   that is the fact a forward test has to price, not the full-sample mean. Note also that this is
   the era with the *best* absolute returns on both legs (+11.08 / +11.97 %/yr) and the shallowest
   leg drawdowns (−22.69 / −17.32): a strong beta era with a thin spread, not a bad era.
4. **Read with the tilt correction.** E40-LADDER-STYLE-EXPOSURE showed the ladder carries a 612bp/yr
   size tilt with beta 0.62 and −19.5bp/month alpha net of it. The era numbers above are raw spread,
   not size-neutral.

## Honest limits

- Eras are partitions of one continuous curve, re-based per slice: era ann% are not additive and do
  not compound to the full-sample figure.
- The last era is open-ended (2024-01-01 → cutoff) and the shortest, hence the least stable.
- Each era cut is a post-hoc calendar choice — four buckets chosen for interpretability, not fitted.
- Descriptive census only: zero prereg, zero judgment, zero ledger booking, trial_count 0.