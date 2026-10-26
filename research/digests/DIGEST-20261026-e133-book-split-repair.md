# E133 — what the split-print repair is worth on the published ETF book, and a count that was lying

2026-10-26 · bm-c r1282 · tool `scripts/etf_book_split_audit.py` (selftest 20/20) ·
evidence `results/etf_book_split_audit/AUDIT-2026-10-23.json`

## The question nobody had priced

The production card (12 names of a 1499-instrument bond-free pool, 20-bar grid, 10bp/side,
8% vol rule, decide-at-close / fill-at-next-open) prints **9.47% CAGR / 0.978 Sharpe /
-11.77% max drawdown / 10.18% realised vol** on a panel whose prints past ±35% have been
flattened and rescaled. Every research face in the E81 line was audited against that repair
(calendar cost, size-neutral spread, robustness grid) — the money surface never was. This
round publishes the raw twin beside the untouched card.

## Result

| arm | CAGR | Sharpe | max DD | vol |
|---|---|---|---|---|
| **repaired (published)** | **9.47%** | **0.978** | **-11.77%** | 10.18% |
| raw (no repair) | 8.30% | 0.857 | -11.77% | 10.32% |
| legacy repair (pre-r1282 code) | 9.47% | 0.978 | -11.77% | 10.18% |

- Repair is worth **+1.17pp of CAGR and +0.121 of Sharpe** (IS +1.11pp, OOS +1.26pp — the
  same in every window), and **exactly 0.00pp of drawdown**: the four prints that reached
  the book all sat inside drawdowns set elsewhere, so the repair flattered nothing on the
  risk side.
- **164 prints** past the threshold inside the production universe; **only 4 ever in the
  book** (the book holds 12 names and re-decides every 20 bars). Those four carry the whole
  2001bp of raw charge:
  - 2020-11-06 `159966` -68.3% (ratio 3.151) and `159967` -73.0% (ratio 3.708) — same day,
    same family, **59% of the total charge**;
  - 2022-03-30 `513500` -49.2% (2:1), 2025-07-07 `512800` -49.7% (2:1).
- **Ratio test vs persistence test**: only 77/164 (47%) land near an integer ratio, so the
  E75 integer-ratio heuristic would have called three of the four in-book corporate
  actions a "resumption or misprint". The decisive test is **level persistence** — take
  the next priced closes and ask whether they stay at the new level (all 164 persist, zero
  revert). Ratio is evidence; persistence is the verdict.

## The defect this audit found on the way

`A.repair_flips` measured returns with `close.pct_change()`. **pandas 3 no longer fills
across a suspension bar**, so a split print that follows one comes back NaN: the level
rebuild still flattened it (NaN floors to a 0% day) but the printed count missed it —
`134` reported against `168` measured against the previous *priced* close — and a small
real move on such a bar was dropped along with it. Fixed in `etf_equity_alpha.py` (measure
against `close.ffill()`, the E74 lesson at a new face); the card was regenerated and prints
`168`. Both panels are now checked for **zero residual prints past the threshold**, and the
legacy arm is kept as a priced counterfactual (`legacy_equals_published: false` on the
curve, i.e. the fix does change bars — the headline happens to be identical).

## Rules worth keeping

1. A repair is a claim until it is priced: publish the raw twin and the delta beside it.
2. `max - min` across arms cannot see a shift, and **a repair can move CAGR without moving
   the drawdown** — read return-impact and risk-impact separately (E81 third face).
3. Measure a threshold's own output: `prints_surviving_in_repaired_panel == 0` is the gate
   that turns "we repaired" into "we repaired all of them".
4. When a heuristic (integer ratio) and a physical test (level persistence) disagree, the
   physical test wins and the disagreement is the finding, not noise.

## Not verified this round

The E130 bridge, the equity-alpha headline and the E81 leg-1..3 faces were computed before
the count fix. The fix is arithmetically neutral for them (same NaN→0 flattening), but none
of them was re-run here; they should be refreshed with the new `repair_flips` before their
numbers are quoted again.