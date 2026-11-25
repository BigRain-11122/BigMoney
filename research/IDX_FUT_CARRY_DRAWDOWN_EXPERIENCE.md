# What it feels like to hold each rung

generated 2026-11-25T22:54:41+08:00 | cutoff 2026-11-25 | schema `idx-fut-carry-drawdown-experience/v1`

## One sentence

`research/IDX_FUT_CARRY_LADDER_RISK.md` prices each rung's risk as vol and drawdown **depth**; here is the same book in the units a client lives in -- the worst month on the statement, the share of positive months, how long the equity stays underwater and how many bars the max-drawdown trough takes to heal. On the instructed rung **1/1** the worst month is **-5.03%**, **78%** of months are positive, the longest underwater run is **120 bars** and the worst drawdown recovers in **114 bars**; Calmar (return per unit of felt drawdown) is **2.430**.

## The band question, in felt terms

The 8-12% band's only feasible rung is **0/1** (expected 9.05%).  Against the instructed **1/1**:

| axis | instructed 1/1 | in-band 0/1 | better |
|---|---|---|---|
| worst month % | -5.03 | -1.34 | **band** |
| positive-month share | 78.4% | 76.5% | instruction |
| longest underwater (bars) | 120 | 135 | instruction |
| max-drawdown recovery (bars) | 114 | 11 | **band** |
| Calmar (ann / |MDD|) | 2.430 | 2.953 | **band** |

Verdict: **BAND_CUT_MIXED_EXPERIENCE** (3/5 axes favour the band).

## Cross-face reconciliation

`research/IDX_FUT_CARRY_LADDER_RISK.md` reports the instructed rung's annual return as **22.34%**; this face reports **26.67%** (4.331 pp apart). The gap is a double-scaling in that face: it builds the equity-sleeve daily contribution as `m = k*sleeve` and then multiplies by `k` again (k^2), under-weighting the sleeve (0.189 instead of 0.435). The rung return is `k*sleeve + (notional/nav)*spread` -- a single `k` -- which is what this face uses. Verdict **CROSS_FACE_DOUBLE_SCALED** (recorded here, not repaired there: that face is another window's shared surface during a contention window).

## Every rung, in felt terms

| rung | exp % | ann % | MDD % | worst mo % | +mo % | longest UW | recovery | Calmar |
|---|---|---|---|---|---|---|---|---|
| 0/0 | 5.17 | 6.36 | -4.71 | -1.17 | 61% | 166 | 117 | 1.351 |
| 0/1 | 9.05 | 17.92 | -6.07 | -1.34 | 76% | 135 | 11 | 2.953 |
| 0/2 | 12.94 | 30.03 | -10.59 | -3.26 | 80% | 107 | 101 | 2.836 |
| 0/3 | 16.82 | 42.62 | -15.66 | -5.48 | 80% | 118 | 112 | 2.722 |
| 1/0 | 13.49 | 14.72 | -6.75 | -2.83 | 78% | 108 | 106 | 2.183 |
| 1/1 | 17.38 | 26.67 | -10.97 | -5.03 | 78% | 120 | 114 | 2.430 |
| 1/2 | 21.26 | 39.10 | -16.05 | -7.23 | 80% | 122 | 116 | 2.436 |
| 1/3 | 25.14 | 51.95 | -20.92 | -9.45 | 80% | 146 | 140 | 2.483 |
| 2/0 | 21.81 | 23.17 | -13.02 | -7.18 | 80% | 140 | 139 | 1.779 |
| 2/1 | 25.70 | 35.44 | -16.84 | -9.37 | 80% | 154 | 129 | 2.105 |
| 2/2 | 29.58 | 48.13 | -21.48 | -11.58 | 82% | 157 | 151 | 2.241 |
| 2/3 | 33.46 | 61.16 | -26.15 | -13.79 | 82% | 157 | 151 | 2.339 |
| 3/0 | 30.14 | 31.63 | -19.14 | -11.66 | 80% | 162 | 161 | 1.652 |
| 3/1 | 34.02 | 44.15 | -22.98 | -13.85 | 80% | 162 | 137 | 1.921 |
| 3/2 | 37.90 | 57.02 | -27.33 | -16.05 | 82% | 165 | 140 | 2.086 |
| 3/3 | 41.78 | 70.15 | -31.55 | -18.25 | 80% | 166 | 141 | 2.224 |

## What is a declaration here

- the rung series compounds the equity sleeve at the ladder's `k`; the sleeve daily series is rebuilt at run time and `check` pins it by digest, not re-derivation;
- monthly compounding drops the first and last calendar month (partial edges); `month_edges_dropped` on every rung names them;
- 51 months used on the instructed rung; all rungs share the same date grid.

