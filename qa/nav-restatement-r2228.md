# QA evidence — r2228 ETF NAV restatement face

Date: 2026-11-28T23:2x+08:00 · machine bm-c · round 2228
Face: `scripts/etf_nav_restatement.py` → `results/etf_nav/restatement.json` + `research/ETF_NAV_RESTATEMENT.md`
Verdict published: `THE_DISPLACEMENT_IS_THE_NAV_DAY_AND_IT_IS_SMALL_ON_MEDIAN`

## What this face claims

A premium print is `close / NAV(nav_session) - 1`. A later print carries the NAV
level for the session it prices, so the NAV a lagging row was missing can be
recovered without any external source. With `r` = that session's NAV return:

    printed - true = r * (1 + true)

i.e. a stale denominator does not add noise; it displaces the reading by one
whole NAV day.

## Commands run (all in `quant/bigmoney`)

| command | rc | evidence |
|---|---|---|
| `python scripts/etf_nav_restatement.py selftest` | 0 | `27 legs, 0 failed` |
| `python scripts/etf_nav_restatement.py run` | 0 | writes both faces |
| `python scripts/etf_nav_restatement.py check` | 0 | `CHECK OK: restatement.json matches a fresh derive from the same inputs` |

## Numbers the face published

| item | value |
|---|---|
| prints measured | 6,505 |
| lagging prints still unmeasurable | 119 |
| prints that needed no correction (same-day denominator) | 13,678 |
| median abs misstatement | **0.58 pp** |
| p90 abs misstatement | 1.63 pp |
| worst | 11.87 pp (512040 · 2023-12-13) |
| identity residual, max over 6,505 rows | **5.0e-07 pp** |
| median error, days the NAV moved < 0.5% | 0.23 pp |
| median error, days the NAV moved ≥ 2% | 2.47 pp |
| r2227 band contained the truth | 5,141 of 6,490 (79.2%) |
| prints excluded as split/distribution (>35% NAV day) | 1 |

Per leg (median abs misstatement): 159519 0.63 pp · 159655 0.54 pp ·
510760 0.51 pp · 512040 0.58 pp · 513690 0.66 pp.

## Self-test coverage (what would fail if the code were wrong)

- `implied-nav-exact` / `implied-nav-guard` / `implied-nav-bad-input`
- `t+1-all-lag`, `last-print-unmeasured`, `true-premium-arithmetic`,
  `error-is-printed-minus-true`, `error-is-this-sessions-nav-move`
- `flat-nav-no-error` (flat NAV ⇒ zero displacement)
- `same-day-not-measured` (negative control)
- `unmeasured-not-zero` / `unmeasured-verdict` / `unmeasured-statement-says-so`
- `no-self-recovery` (a level must not come from a print at or before its session)
- `tapes-are-per-leg` (two legs printing the same day must not share a denominator —
  this leg was added after the first implementation mixed them and produced a
  bogus +100% "true premium" on 512040)
- `band-counts-inside` / `band-counts-outside` / `band-no-history-is-not-a-pass`
- `split-excluded-not-measured`
- `verdict-nothing` / `verdict-big-clean` / `verdict-big-dirty` / `verdict-small-clean`
- `e2e-measured-three` / `e2e-identity-clean` / `e2e-statement-names-worst`

## Known limits (printed in the face, not hidden)

- The 35% guard removes share conversions; an ex-dividend day (price **and** NAV
  jump together) is counted as a misstatement because from the reader's side it
  is one, but its cause is the distribution. No ex-dividend flag exists in this
  repo, so the two causes are not separated.
- The deep sample is the five legs in `results/etf_premium/premium_history.csv`.
  The 1,670-leg snapshot series is scanned by the same code; today it can
  recover nothing, because a one-off lag heals by using the *next* session's
  NAV, so the missing level never appears in a print.
- Nothing here sizes a position.
