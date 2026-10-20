# DIGEST 2026-10-21 — E38 panel-drift census: the wide-book number is a panel snapshot, now measured (bm-b r1111)

r1110 ended with a claim and an inference: "three panel states, one spec, three magnitudes
(82.7 / 156.0 / 215.5)". This round turns the inference into a recorded measurement, and it caught
the drift live — mid-round, minute-scale, on an unchanged spec.

Everything here is descriptive census: zero prereg, zero judgment, zero ledger booking, trial_count 0.

## 1 — The drift, caught in the act

The E29 universe pass landed its last files *during* this round:

| local time | probe | panel current | vs ladder (bp/yr) | t | eligible @ 2026-10-20 |
|---|---|---|---|---|---|
| 03:44:17 | coverage report | 1,670 / 1,725 | — | — | — |
| 03:45 | e27 run, same spec | — | **+138.9** | 0.63 | 1,183 |
| 03:47:5x | coverage report | 1,723 / 1,725 | — | — | — |
| 03:48 | e27 run, same spec | — | **+133.7** | 0.61 | 1,223 |

Same command, same window (2020-01-01 → 2026-10-20), same exclusions. In roughly two minutes the
panel gained 53 current files, the eligible count at a **fixed** date moved by **40 members**, and
the annualised spread moved **5.2 bp**. That is first-order, not noise.

Once arrival stopped, the identical command reproduced the identical numbers exactly: two consecutive
census runs agree to the digit (133.7 bp / 1190 eligible at the reference date, both runs).

**Consequence: a wide-book magnitude is only quotable together with its panel coverage state.**
2026-10-21T03:47, coverage 1,723/1,725, is the first converged state worth quoting.

## 2 — Cut axis: six month-end truncations of one spec

Spec: `e27_universe_expansion --exclude sh511 --ns 9999 --start 2020-01-01`, sh511 excluded,
1,265-code universe.

| cut | bars | years | vs ladder (bp/yr) | t | eligible at cut |
|---|---|---|---|---|---|
| 2026-03-31 | 1,502 | 5.96 | +206.4 | 1.23 | 989 |
| 2026-06-30 | 1,564 | 6.20 | **-15.4** | -0.01 | 1,097 |
| 2026-08-31 | 1,607 | 6.37 | +91.6 | 0.44 | 1,168 |
| 2026-09-22 | 1,631 | 6.47 | +82.7 | 0.41 | 1,190 |
| 2026-09-30 | 1,637 | 6.49 | +106.0 | 0.51 | 1,198 |
| 2026-10-20 | 1,645 | 6.53 | +133.7 | 0.61 | 1,223 |

Spread across cuts: **221.8 bp**, and the sign flips (2026-06-30 is -15.4). Every t is below 1.3.

The cut axis mixes two things by construction — window length and period luck — so it cannot by
itself separate "panel state" from "sample period". The column that *does* isolate panel state is
`eligible at ref`: at the fixed reference date 2026-09-22 the count is **1,190 under every cut that
covers that date** (four of them). That is the convergence proof: with the panel settled, the same
date yields the same membership no matter where the run is truncated.

## 3 — Cost axis: fees are not the fragile part

| cut | x1 (bp/yr) | x3 (bp/yr) | move |
|---|---|---|---|
| 2026-09-22 | +82.7 (t 0.41) | +76.9 (t 0.39) | -5.8 |
| 2026-10-20 | +133.7 (t 0.61) | +127.6 (t 0.59) | -6.1 |

Tripling every side's cost moves the read by ~6 bp — the same ~6.6 bp r1110 measured on the
pre-convergence panel. **The fragility of this number lives in the data, not in the fees.** An
edge this thin cannot be rescued or destroyed by a cost assumption; it is dominated by which members
happened to have files.

## 4 — What this settles and what it does not

Settled:
- the r1110 985 → 1,190 paradox was **panel arrival**, not a spec artefact — the count is now
  cut-invariant at a fixed date;
- the +215.5 / +156.0 / +82.7 spread was **panel state**, not strategy drift;
- cost sensitivity is ~6 bp on both a converged and a frozen slice, so fees are a second-order face.

Not settled (and now correctly framed as unanswerable on this panel):
- whether the wide book's ~+134 bp/yr is a real edge. It is t 0.61 on the converged panel: this is
  a **non-result**, and no amount of re-cutting will change that. The wide-book line stays marked
  unstable until it is measured on a panel with a refresh *history* (a panel that can be replayed
  as-of, not just read once), or until the ladder itself is beaten at a t that clears noise.

## Products

- `scripts/e38_panel_drift_census.py` (selftest 7/7, two-run byte-identical)
- `results/e38_panel_drift_census/CENSUS-20261020.json`, `cuts.csv`, `cut_axis.json`
- `results/e38_panel_drift_census/ARRIVAL-TRACE-20261021.json`
- `results/e38_base_converged/UNIV-4170ac-s20200101-e20261020-xsh511-20261021.json`
- `results/panel_coverage.json` + `docs/panel_coverage/COVERAGE-20261020.md` (1,723 / 1,725 current)

## Handoff

Do not draft a wide-book prereg on this panel. The remaining honest work on this family is
panel-observability (as-of replay), not another N sweep — the N axis was answered at r1110 and the
panel axis is answered here.