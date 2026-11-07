# DIGEST — zoo #93 CGO, judged on the only leg an A-share desk can hold (r1408 bm-c)

Prereg: `research/CASE_PREREG_ZOO93_TAKEABLE.md` (frozen before the first run).
Judge: `scripts/zoo93_disposition_cgo_judge.py` (selftest 14/14).
Face: `results/supply_berth/zoo93_disposition_cgo_judge.json`.
Card: E411. Builds on the supply berth `results/supply_berth/zoo93_disposition_cgo_probe.json` (r1393, ADMIT_TO_PREREG).

## Why this round exists

r1393 priced the Grinblatt–Han capital-gains-overhang berth as a **decile spread** and returned
ADMIT_TO_PREREG: low-CGO decile +0.2717 % per 20 bars, high-CGO decile −0.5130 %, spread net
+0.2631 %, z = 38.2 against a same-size random-group null. 65 % of that spread sits on the
**short** leg, and a single stock cannot be shorted in A-shares. The probe said so itself and
stopped: a supply berth buys a prereg, not a profit claim. Nothing had asked whether the
takeable half is worth doing.

## What was measured (frozen construct, no tuning)

Panel `data/astock_daily/per` 5,197 names, evidence cutoff 2026-10-30; CGO = turnover-attenuated
60-bar cost basis; liquidity gate 20-bar median amount ≥ 20 M CNY (the book's own `MIN_AMT`);
20-bar non-overlapping cohorts, entry at `open[d+1]`, equal weights, costs 13.041 bp/side at x1
and x3, four decision grids (offsets 0/5/10/15 bars). Span of the traded cohorts 2020-07-03 →
2026-09-07 (78 cohorts per grid).

| arm (grid 0) | CAGR x1 | CAGR x3 | Sharpe x1 | maxdd x1 | names |
|---|---|---|---|---|---|
| `decile` (bottom 10 % of CGO) | **+10.09 %/yr** | +5.55 %/yr | 0.46 | −30.7 % | 428 |
| `n50` (50 lowest CGO) | +9.33 %/yr | +4.06 %/yr | 0.42 | −31.0 % | 50 |
| `pool` (all liquid candidates) | **+9.24 %/yr** | +8.76 %/yr | 0.46 | −27.4 % | 4,283 |
| `510300` buy & hold | **−0.20 %/yr** | −0.29 %/yr | −0.01 | −45.1 % | 1 |

Excess over the pool, per decision grid:

- `decile` x1: +0.90 / +1.50 / +2.00 / +3.00 pp/yr → **4/4 positive, median +1.71**
- `decile` x3: −3.20 / −2.60 / −2.10 / −1.10 pp/yr → **0/4 positive**
- `n50` x1: +0.10 / +0.80 / +4.70 / +0.90 → 4/4 positive, median +0.89; x3 0/4

Index-timing reading of the same number (aggregate overhang = cross-sectional median CGO, gate =
its own trailing 252-bar percentile, both signs frozen up front):

| arm | CAGR x1 | long share | maxdd | null p (200 state rotations) |
|---|---|---|---|---|
| `gate_low` (cheap overhang ⇒ long) | +1.52 %/yr | 11.0 % | −6.8 % | **0.289** |
| `gate_high` (rich overhang ⇒ long) | −3.92 %/yr | 8.5 % | −23.4 % | 0.965 |

## Verdict

`REFUSE_AS_CANDIDATE` — no takeable arm clears the frozen bar (≥ +1.00 pp/yr at x1, > 0 at x3,
positive on ≥3/4 grids):

- `decile` earns +1.71 pp/yr at ETF-grade cost and **loses 3.2 pp/yr at x3**: the edge is smaller
  than the difference between the two cost assumptions, so it is not a money claim.
- `n50` is the same story one size down (+0.89 at x1, 0/4 at x3).
- `gate_low` returns 1.5 %/yr while in the market 11 % of the time, and its own state rotations
  beat it often enough that p = 0.289: the low-overhang periods it picked were not good periods.

Two readings worth keeping even though the verdict is negative:

1. **The breadth premium dwarfs factor selection in this sample.** Equal-weighting every liquid
   A-share returned 9.24 %/yr with a −27 % drawdown over a span in which 510300 returned −0.2 %/yr
   with a −45 % drawdown. Any stock-factor discussion that starts from the index as its benchmark
   is measuring the wrong thing — the pool, not the index, is what a long-only stock desk is
   compared against.
2. **The short leg is where the money is, and it is not takeable.** 65 % of the r1393 spread sits
   on names an A-share desk cannot sell short; the long-only remainder is inside the cost model.

## A defect caught in the judge itself (card E411)

The first run reported `gate_low` null p = 1.000 with an sd of 3.2e-19. A circular rotation of a
**realised net series** is a permutation, so its mean is exactly invariant — every draw equals the
actual, and any rule reads p = 1.000. The null must rotate the **state against the returns** and
re-price the costs on the rotated state. After the fix the same arm reads p = 0.289, i.e. the
reading that was hidden was the important one.

## Next

The supply board is now empty of registered berths *and* of judged ones. `#97 etf_premium_sentiment`
remains blocked on a premium panel; the honest next step is a new frozen prereg, not another pass
over this family (a re-burn of the same construct with a different cost constant is the r1325
"phase accident" trap in a new dress).