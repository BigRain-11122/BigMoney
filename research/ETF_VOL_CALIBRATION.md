# ETF book: can the 8% vol label be made TRUE, causally?

Status: **verdict HOLD** (label reported, not corrected). Engine: `scripts/etf_vol_calibration.py`
(`run` / `--selftest`, 12 legs). Evidence: `results/etf_vol_calibration.json`, cutoff
2026-10-23. Frozen production config throughout: 12 names of the bond-free pool, 20-bar
decision grid, 10bp/side, decide at close *t* -> fill at open *t+1* -> hold to next rebalance.

## The question

r1272 decomposed the 8% label vs 10.18% delivered vol and reported it rather than patch it,
because a multiplier fitted on the same sample is the fitting the earlier sweeps exist to
detect. The open question is whether it can be fixed *causally*: at every decision, knowing
only (a) the estimator the engine just produced and (b) the realised vol of holds that have
already CLOSED, can we size so that the delivered figure is the number on the label?

## What was tried

`WalkForwardCalibration` keeps a queue of decisions. A hold at decision *i* runs from the open
of bar *i+1* to the open of bar *i+20*, so its realised vol becomes knowable exactly at the
next hook call; settlement therefore happens then, and the current decision never sees its own
outcome. The multiplier `m` is formed from `MIN_OBS=6` completed holds onward (m=1.0 before
that, i.e. the published behaviour) and divides the sizing denominator:

    scale = min(cap, target / (est * m))

Two estimators of `m` were run, both causal:

* **median** of past ratios `realised/est` — "the typical hold".
* **rms** of past ratios — the multiplier a *mixture variance* target actually needs.

## Result

| arm | delivered vol (full) | delivered vol (OOS) | Sharpe | maxDD | CAGR |
|---|---|---|---|---|---|
| A no target (reference) | 15.31% | 14.81% | 0.970 | -15.9% | 14.03% |
| B published (m=1) | 10.18% | 10.45% | 0.978 | -11.8% | 9.47% |
| C causal median calibration | 9.91% | 9.89% | 0.992 | -11.5% | 9.38% |
| D calibrated, cap 3.0 | 10.07% | 10.17% | 0.991 | -12.2% | 9.52% |
| **E causal rms calibration** | **8.08%** | **8.22%** | 0.946 | **-9.8%** | 7.27% |

Median calibration barely moves the label (10.18% -> 9.91%, m median 1.06) even though it is
active for 93% of decisions. The rms calibration lands within 0.1pp of the label in the full
window and 0.2pp OOS, cuts max drawdown from -11.8% to -9.8%, and costs 0.032 of Sharpe
(0.978 -> 0.946) plus 2.2pp of CAGR, because average invested scale falls 0.71 -> 0.55.

## Why the median version could not work (the actual finding)

Delivered annualised vol over a sample of holds is **the root-mean-square of the sized segment
vols, not their mean**. Measured against the arm's own decisions:

| quantity | published arm |
|---|---|
| hold vol, mean | 13.62% |
| hold vol, rms | 15.35% (dispersion rms/mean **1.13**) |
| sizing x hold vol, mean | 9.16% |
| sizing x hold vol, rms | 10.19% |
| measured annualised vol | 10.18% (identity error **0.01pp**) |
| ratio realised/est, median | 1.06 |
| ratio realised/est, rms | 1.30 (**rms/median 1.22**) |

So of the 2.18pp gap between the label and the delivered figure, the estimator's *median*
bias is worth about 0.06x and the *dispersion* of the realised ratio (rms/median 1.22) is
worth the rest. A rule sized on the median ratio therefore undershoots by construction: it
makes the typical hold 8%, which annualises to 8% x 1.22 = ~9.8%. This also corrects the
framing r1270/r1272 left open: the sleeve is not "27% riskier than its label" in the sense of
bad sizing; an 8%-per-hold target *is expected* to annualise near 10% once hold-level vol
dispersion is accounted for. The label and the delivered number measure two different things.

To deliver 8% annualised the mean hold vol has to be ~6.2% = 8%/1.29.

## Pre-stated adoption rule and verdict

Stated before the numbers were produced: (1) delivered vol within 1.0pp of target in both
full and OOS; (2) full-window Sharpe no worse than published by more than 0.02; (3) the
calibration active for >=50% of decisions; (4) multiplier drift between halves <= 50%.

| leg | result |
|---|---|
| vol within 1.0pp | PASS (8.08% / 8.22%) |
| Sharpe not worse by >0.02 | **FAIL** (0.946 vs 0.978 = -0.032) |
| calibration active | PASS (92.8% of decisions) |
| ratio stable | PASS (drift 6.3%, m median 1.31, halves 1.38/1.29) |

**HOLD**: one leg fails, so the card keeps reporting the gap instead of adopting the
calibration. The failure is narrow and is a risk/return trade rather than a defect: the
mixture-aware rule buys a truthful label and 2pp less drawdown for 0.03 Sharpe and 2.2pp of
CAGR. Adopting it is a policy decision for the GM/CEO (do we want a risk label that is
literally true, at a measurable cost in stated return?), not a research finding.

## What this changes on the card

Nothing mechanically. The card already prints `target 8% -> delivered 10.2% (1.27x)`; from
this round that line should be read as a *definition gap*, not as an estimator failure, and
the caveat text on the card is updated to say so. When the label is next re-stated it should
either say "8% per hold (annualised sample vol ~10%)" or move to the rms sizing.

## Reproduce

    python scripts/etf_vol_calibration.py run
    python scripts/etf_vol_calibration.py --selftest     # 12 legs, incl. a no-lookahead leg

The no-lookahead leg is the load-bearing one: the calibrated arm is re-run on a panel with the
last 260 bars removed, and every decision the two runs share must produce an identical scale
(measured: 70 decisions, max difference 0.00e+00). The engine change is `ratio_hook` on
`etf_robust_pf.open_to_open_equity`, whose `None` default is bit-identical to the published
overlay (maxabs 0.00e+00, turnover 0.934317 both).