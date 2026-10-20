# DIGEST — Seasonal horizon & stability census (E23, 2026-10-20)

**One line.** E22's calendar windows were measured on pooled stock-days; re-measured on a
*daily equal-weight face* (one observation per trading day, so cross-sectional correlation no
longer inflates the t), the month-first-day excess shrinks from +41.8bp to **+22.3bp and does not
survive round-trip cost** — while the pre-holiday window, held ~4 bars, is the one cell that is
both cost-positive and era-stable.

- Product: `scripts/seasonal_horizon_stability.py` (selftest 19/19, deterministic L1, 2.8s rerun;
  rerun identical except the `generated` wall-clock field — verified by hashing all other fields)
- Evidence: `results/seasonal_horizon_stability/CENSUS-2026-10-19.json` (+`by_horizon.csv`, `latest.json`)
- Face: panel `data/cache/p1c_local`, 5,225 symbols × 8,745 dates, 1990-12-19 → 2026-10-19
  (cutoff = expected), 8,638 usable days, 16,583,153 usable stock-days, baseline **+9.39bp/day,
  win 54.1%**. Exclusions identical to E22 (bad px / suspension-resume / one-price / |r|≥75%).
- Scope: **descriptive only** — zero prereg, zero judged face, zero pool write, zero network.
  45 cells (9 variants × 5 horizons), uncorrected: no multiplicity claim.

## What changed vs E22

| reading | E22 (pooled stock-days) | E23 (daily face) |
|---|---|---|
| tom_start1 (month's first day) | +41.8bp, win 56.7%, 24/36 years | **+22.3bp, t=+1.44, win 61.6%** |
| tom_end2 (second-to-last day) | −28.9bp, 8/36 years | **−30.7bp, t=−2.78, win 46.9%** |
| hol_post1 | +35.3bp | +27.2bp (t=+1.20) |
| hol_pre1 | +30.7bp | +26.5bp (t=+1.92) |

The negative half of the folk claim **survives** the daily-face correction (t=−2.78); the positive
half loses most of its magnitude. E22's inflation caveat is now quantified, not just disclosed.

## Cost is what kills the monthly windows

A monthly timing overlay switches ~12 times/year (431 spells over 35.8 years); one switch costs
2 × 13.041bp = 26.1bp, i.e. **3.14%/yr of cost**. Gross vs net, h=1:

| variant | gross %/yr | cost %/yr | **net %/yr** | years above baseline |
|---|---|---|---|---|
| tom_start3 | +4.19 | 3.14 | **+1.05** | 22/37 |
| tom_start1 | +2.64 | 3.14 | **−0.50** | 24/36 (24/36 in E22 too) |
| tom_end1 | +1.73 | 3.14 | **−1.41** | 20/36 |
| tom_end2 | −3.65 | 3.14 | **−6.79** | 8/36 |
| hol_post1 | +1.37 | 1.32 | **+0.04** | 20/35 |
| hol_pre1 | +1.33 | 1.32 | **+0.01** | 24/35 |

So the honest statement is: **month-first is a real 22bp/day tilt, but a pure monthly switch
overlay pays it away.** The only monthly cell left positive (tom_start3) is not era-stable —
2024-2026 runs **−48.5bp** against pre-2017 **+14.3bp**.

## Horizon (the actionable part)

Cumulative excess by holding period, days where a window was used all-h:

| variant | h=1 | h=3 | h=4 | h=5 |
|---|---|---|---|---|
| hol_pre1 | +26.5bp (t 1.92) | +69.5 (2.03) | **+103.4 (3.02)** | +75.6 (1.83) |
| hol_post1 | +27.2 (1.20) | **+75.2 (2.56)** | +47.5 (1.32) | +65.3 (1.61) |
| tom_start1 | +22.3 (1.44) | **+72.4 (2.89)** | +63.6 (2.14) | +83.8 (2.42) |
| tom_start2 | +17.5 (1.29) | +50.2 (2.12) | +60.6 (2.29) | +69.4 (2.30) |
| tom_end2 | −30.7 (−2.78) | +7.4 (0.32) | +20.4 (0.79) | +59.6 (2.00) |

Two structural facts a drafter must carry: (1) the excess **accrues over ~3-4 bars, not on day 1**,
which is exactly why amortising the switch cost over a multi-day hold is the only viable
expression; (2) tom_end2's −30.7bp decays to flat by h=3 — the "avoid month-end" advice is a
one-day effect, not a window.

## Era / decay (h=1 excess, bp)

| variant | pre-2017 | 2017-20 | 2021-23 | 2024-26 | decay slope (bp/yr) |
|---|---|---|---|---|---|
| hol_pre1 | +32.4 | +15.6 | +60.2 | **+60.8** | −1.2 |
| hol_post1 | +37.0 | −29.4 | +67.2 | +21.4 | +0.5 |
| tom_start1 | +13.8 | +27.3 | +65.2 | +58.4 | +1.9 |
| tom_start3 | +14.3 | +20.5 | +20.5 | **−48.5** | +1.8 |
| tom_end2 | −33.5 | −51.0 | −15.7 | +7.0 | −0.4 |

No monotone decay anywhere; the windows are regime-conditional, not a stable anomaly. hol_pre1 is
the only variant positive in **all four** eras.

## Honest limits

- Overlapping windows at h>1 are autocorrelated; t for h>1 is still optimistic (only h=1 is
  genuinely a one-observation-per-day series).
- 45 cells, uncorrected — the hol_pre1 h=4 (+103bp, t=3.02) being the best cell is **post-hoc
  selection**, not a pre-registered claim. Any use must re-derive it out-of-sample.
- Equal-weight face is an index proxy, not a tradable instrument; costs use the frozen
  `COST_X1_RATE` (13.041bp/side) with no slippage/impact model.
- Holiday windows depend on the ≥4-calendar-day break rule (182 breaks), which is a heuristic.

## Consumer hand-off (W22 draft input)

1. **Do not** draft a monthly-switch family: cost-negative at h=1 for every turn-of-month cell
   except tom_start3, which fails era stability.
2. **Do** draft the seasonal family on the pre-holiday window with an explicit multi-bar hold
   (h≈4) exit axis — the only cost-positive, all-era-positive cell — and carry hol_pre1 h=4 as a
   *candidate*, not a finding.
3. Freeze in the prereg: exit axis = "hold N bars from the pre-holiday entry, no engine default
   exit" (TRIAL_LABOR_LAW §4 option ①), N tested as a declared grid (not selected post-hoc), and
   a D6 check vs fund_divlowvol / rev_osc before registration.