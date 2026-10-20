# E43 triad — four-member reach-back, wide-book composition, size-neutral robustness

Evidence cutoff 2026-10-20. Engine: `e24_ladder_weighting` / `e27_universe_expansion`
(module import, unchanged). Script: `scripts/e39_panel_census.py` (`e43` mode, selftest 44/44).
Descriptive census only: zero prereg, zero verdict, zero ledger booking, trial_count 0.

## 1. E43-TILT-4MEMBER-HISTORY — the reach-back is a 2017-2020 win, not a 2013 one

`results/e43_tilt_4member/HIST-20261020.json`

Dropping the STAR leg (2 broad-cap vs 510500/512100, weights 0.5/0.5) does unlock the
2017-2020 era: **48 usable months, up from 1 on the five-member skin**. It does *not*
unlock pre-2017 — that era still carries exactly 1 month, because the binding constraint
after removing sh588000 is not the member bars but the engine curve's own start
(the wide book's full-sample monthly series begins 2016-12). So the E43 premise is half
right: the STAR leg was one of two constraints, and the second one is the book's
eligibility burn-in, not the panel.

| era | months | tilt bp/yr | beta ladder on tilt | R2 | raw spread bp | size-neutral bp | beta spread on tilt |
|---|---|---|---|---|---|---|---|
| pre2017 | 1 | — | — | — | — | — | — |
| 2017-2020 | 48 | -993.3 | 0.321 | 7.4% | +331.7 | **+293.7** | -0.038 |
| 2021-2023 | 36 | +953.6 | 0.161 | 3.5% | +251.1 | **+394.1** | -0.150 |
| 2024-now | 34 | +246.5 | 1.197 | 57.7% | -35.1 | **+38.5** | -0.298 |
| full | 119 | -38.1 | 0.507 | 17.1% | +215.8 | **+209.8** | -0.159 |

The sign of the tilt flips: small caps *underperformed* broad by 993bp/yr in 2017-2020 and
*outperformed* by 954bp in 2021-2023. The full-sample tilt is near zero (-38bp) only because
those two eras cancel — which is why the full-sample neutral (+209.8) and raw (+215.8) are so
close, and why any era-level reading must be read on its own months.

Skin comparison on identical months (the STAR leg's price):

| era | tilt 5-member | tilt 4-member | same months |
|---|---|---|---|
| 2021-2023 | +609.2 | +953.6 | yes (36) |
| 2024-now | +748.1 | +246.5 | yes (34) |
| full | +611.9 | -38.1 | no (71 vs 119) |

The STAR leg was a drag in 2021-2023 and the whole story in 2024-now: on the five-member skin
the newest-era tilt is +748bp, on the four-member skin +247bp. **The choice of skin moves the
newest-era size-neutral spread from +181.2bp (E42) to +38.5bp (E43)** — a 4.7x cut from a
naming decision, not from the data.

## 2. E43-WIDE-SIZE-COMPOSITION — the beta lives in the 96%, not in the five names

`results/e43_wide_composition/COMP-20261020.json`

At each decision point (160 rebalances, holdings read with the engine's own ranking function
on the engine's own rank cache): mean 302.9 holdings, the ladder's five members are
**3.70% of the book** on average (min 0.41%, max 11.54%), the other 96.3% is everything else.

| bucket | beta on tilt (2024-now) | beta (full) | R2 (2024-now) |
|---|---|---|---|
| wide book | +0.899 | +0.348 | 48.0% |
| residual (universe minus 5) | +0.897 | +0.346 | 47.9% |
| ladder5 | +1.197 | +0.507 | 57.7% |
| spread (wide minus ladder) | -0.298 | -0.159 | 40.6% |

Read: the wide book is *positively* tilted to small caps (+0.899) and the ladder is more
positively tilted (+1.197); the spread's negative beta is the difference of two long tilts,
not the wide book being short small caps. The residual bucket reproduces the wide book's beta
to 0.002, which is the composition proof: with the five names at 3.7% weight, the tilt cannot
be coming from holding them.

## 3. E43-NEUTRAL-ROBUSTNESS — the +181bp newest-era claim does not survive

`results/e43_neutral_robust/ROBUST-20261020.json`

Four decision calendars (month-end-1 / month-end / month-end+1 / first session on-or-after
the 15th) crossed with cost x1 and x3, 8 cells, 4-member tilt, start 2020-01-01:

| cell | newest-era size-neutral bp | full-sample (81m) size-neutral bp |
|---|---|---|
| x1 me_m1 | +36.7 | +172.7 |
| x1 me | +38.5 | +165.6 |
| x1 me_p1 | +9.2 | +151.9 |
| x1 mid15 | +3.8 | +145.5 |
| x3 me_m1 | +29.8 | +167.1 |
| x3 me | +31.7 | +160.0 |
| x3 me_p1 | +2.6 | +146.4 |
| x3 mid15 | -3.3 | +139.7 |

Newest era: 6 of 8 positive, min -3.3bp, max +38.5bp, band 41.8bp — and the two weakest cells
are the mid-month calendar at both cost levels. The only surviving statement is the weaker
one: the *full-sample* size-neutral spread is positive in 8 of 8 cells (139.7-172.7bp), so
the direction is robust while the newest-era magnitude is a calendar-and-skin artefact.

## Carry-forward

- Any E42-style newest-era number should now be quoted with the skin and the calendar named.
- The 2017-2020 era is now measurable (48 months) and is the strongest size-neutral era at
  +293.7bp — the irony being that its raw tilt is negative, so the neutralisation *lifts* it.
- Next seeds if the pool is refilled: pre-2017 remains blocked on the engine curve start, so
  the honest next step is a burn-in-window question (does eligibility burn-in buy the missing
  years?) rather than another member swap.