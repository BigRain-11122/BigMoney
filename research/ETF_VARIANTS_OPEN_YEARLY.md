# ETF composite variants on an honest fill base, with a per-year table (r1247, bm-c)

Answers the two items r1244 left open on `research/ETF_COMPOSITE_SLEEVE_VARIANTS.md`: (1)
its subset numbers were all close-to-close from the decision close, and (2) its 2024+ window
is 2.8 years of one regime, so an OOS excess could be one year wearing a disguise.

Product: `results/etf_variants_open_yearly.json`, code `scripts/etf_variants_open_yearly.py`
(`--selftest` = offline 4/4). Same score, top-5 equal weight, 20-session cadence, 8bp/side on
turnover, panel cutoff **2026-10-23**. Basis switched to next-open fill: decision at close t,
filled at the open of t+1, overnight gap to the OLD book, weight change charged at that open,
NEW book earns open→close on the fill day.

## Table

Each row is the book on that subset, versus its own equal-weight control on the same columns.

| subset (universe) | full CAGR | Sharpe | maxDD | IS 2020-23 | **OOS 2024+** | OOS Sharpe | OOS maxDD | OOS excess vs own EW | years beating own EW |
|---|---|---|---|---|---|---|---|---|---|
| all classes (1,653) | 8.57% | 0.854 | -13.1% | 4.58% | 14.50% | 1.395 | -10.2% | +4.85pp | **5/7** |
| **bond removed** (1,547) | **14.30%** | **0.992** | -16.1% | **9.10%** | **22.06%** | 1.355 | -12.4% | **+13.02pp** | **6/7** |
| equity + gold (1,309) | 7.00% | 0.520 | -22.3% | 3.86% | 11.57% | 0.708 | -22.3% | +2.96pp | 4/7 |
| crossborder removed (1,413) | 8.28% | 0.841 | -15.8% | 2.17% | 17.63% | **1.768** | **-8.2%** | +8.19pp | 5/7 |

Per-year excess (book minus own EW, pp):

| subset | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026* |
|---|---|---|---|---|---|---|---|
| all classes | -18.3 | +10.4 | +16.3 | +13.2 | -7.6 | +1.8 | +15.8 |
| bond removed | -13.1 | +15.0 | +20.5 | +15.4 | +4.7 | +4.9 | +20.0 |
| equity+gold | -15.4 | +2.0 | +26.5 | +2.9 | -11.8 | -9.1 | +23.3 |
| crossborder removed | -21.0 | +4.4 | +16.3 | +11.2 | -8.8 | +15.1 | +16.4 |

\* 2026 has ~200 bars (cutoff 2026-10-23) and is flagged `partial` in the JSON. The flag is
applied to any cell with fewer than 235 bars, on either end of the span, so a truncated year
can never be mistaken for a full one.

## Findings

1. **r1244's "equity+gold is the surviving mechanism" does not survive an honest fill base.**
   Close basis it measured 16.02% OOS (+7.41pp); on next-open it is 11.57% (+2.96pp) and beats
   its control in only 4 of 7 years. The gold sleeve was load-bearing *only* while closing
   prices were free. Conversely `bond_removed` gets **better** under next-open (13.47→14.30
   full, 20.81→22.06 OOS).
2. **The bond-removed edge is not one year.** It beats its own control in 6 of 7 years, and the
   two strongest cells (+20.5pp 2022, +20.0pp 2026) are equity-drawdown years rather than the
   2025 rally (+4.9pp). That is a defence mechanism, not a momentum rally: the book moves to
   gold/cross-border when equity momentum is negative, and it is paid for it in exactly the
   years the equal-weight universe loses 15%+.
3. **2020 is a real failure and it is the same in every variant** (-13 to -21pp): the book
   underperformed a rising, broad, low-quality market by a wide margin. A trend/momentum
   gate is by construction late in a melt-up; nothing in this table fixes that, and any
   forward book has to expect it.
4. **Next-open beating close for rotation books is a mechanism, not free money.** The
   overnight gap on the fill day belongs to the OLD book, so a book that holds winners through
   the gap keeps their drift while a close-to-close book cannot. This is honest arithmetic but
   it is also *unavailable* in real time: the trader cannot choose the fill basis after seeing
   the gap. Treat the next-open number as the upper of two defensible bases, not as the one to
   quote as expected return.

## Parameter platform (same round, `--sweep`, `results/etf_variants_sweep.json`)

The bond-removed book over N ∈ {3,5,8,10} × R ∈ {10,20,60}, next-open basis, each cell
against an equal-weight control rebalanced at **the same R**:

| N \ R | R=10 full / OOS exc | R=20 full / OOS exc | R=60 full / OOS exc |
|---|---|---|---|
| N=3 | 12.57% / +10.62pp | **16.53% / +14.27pp** | 3.76% / +1.44pp |
| N=5 | 13.88% / +11.93pp | 14.30% / +12.04pp | 4.21% / +1.89pp |
| N=8 | 11.30% / +9.35pp | 10.80% / +8.54pp | 1.33% / -0.99pp |
| N=10 | 10.79% / +8.84pp | 9.59% / +7.33pp | 1.27% / -1.05pp |

(OOS excess at each cell: N3_R10 +7.17, N5_R10 +7.00, N8_R10 +11.60, N10_R10 +10.10,
N3_R20 +19.39, N5_R20 +13.02, N8_R20 +13.39, N10_R20 +11.28.)

**The edge lives on the cadence axis, not on the holdings axis.** Every R ≤ 20 cell beats
its control in both windows (8/8); every R = 60 cell collapses to 1.3-4.2%/yr and three of
the four lose to the control outright. Breadth (N) is a secondary knob: 3-5 holdings beat
8-10 in the full window, the reverse out of sample - i.e. N is within noise, R is not.

So the mechanism is specifically *a 2-4 week swing rotation*, and "just hold fewer names
and rotate every quarter" is not the same strategy but a worse one. Consequence for any
real deployment: the book must be re-picked on the ~20-session grid, and that grid is the
thing to protect in execution (missed rebalances degrade the edge directly, not just
slippage).

Honest reading of the best cell (N3_R20, 16.53%/28.43%): do **not** quote it. It is the
maximum of 12 post-hoc cells; the middle of the surviving plateau is N=5/R=20, which is the
number this note has been reporting all along.

## What this does not say

- Exploratory, not preregistered: no verdict, no ledger booking, no promotion.
- Survivorship: the on-disk panel holds ETFs that still exist (1,653 of them).
- Subsets are static: `bond_removed` cannot rotate back into bonds, so it is a different
  strategy, not the published book minus one leg.
- Turnover is 1.25-1.41 per rebalance in every variant, i.e. the books are almost fully
  re-picked each 20 sessions; the cost line is a large share of gross and is charged at the
  fill open, not intra-day VWAP.
- Single published parameter point is N=5, R=20; the sweep above shows the *cadence* axis
  (R≤20 vs R=60) is load-bearing and the *breadth* axis (N) is not.

## Next

- Permutation null on the bond-removed variant (`etf_composite_pf.null_test` currently runs
  on the full panel only), so the p-value reported in r1243 is quoted for the book we would
  trade.
- Rolling-origin / walk-forward pass: every cell here starts 2020-01-01, so a common start
  date is shared by all windows; a rolling origin would separate "works since 2020" from
  "works".
- Fill-timing study: close-fill vs next-open-fill as an explicit lever, with the constraint
  that the choice must be fixed before the gap is observable.