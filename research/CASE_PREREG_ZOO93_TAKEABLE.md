# CASE PREREG — zoo #93 CGO: is any of the decile spread *takeable*?

**FROZEN 2026-11-07T23:1x+08:00 (bm-c r1408), before the first run of the judge script.**
Queue row: none — this consumes the supply berth opened by `results/supply_berth/zoo93_disposition_cgo_probe.json`
(r1393 bm-c, verdict `ADMIT_TO_PREREG`). Card: E411. Probe (read, not re-implemented):
`scripts/zoo93_disposition_cgo_probe.py` → `load_panel`, `cgo_matrix`, `group_readings`.

## 1. What the probe already established, and what it deliberately did not

The probe measured a **decile spread**: bottom-CGO decile minus top-CGO decile, 20-bar hold,
both legs charged two sides at 13.041 bp. Readings (5,197 names, 1,653 bars, 2020-01-02..2026-10-30):

| leg | per 20 bars |
|---|---|
| low decile excess over that date's cross-sectional mean | **+0.2717 %** |
| high decile excess over that date's cross-sectional mean | **−0.5130 %** |
| spread gross | +0.7848 % |
| spread net (4 sides) | +0.2631 % |
| same-size random-group null | −0.0020 pp, sd 0.0206 pp, z = 38.2 |

So 65 % of the gross spread sits on the **short** leg. The probe's verdict was a *supply*
verdict: it buys a frozen prereg, it does not claim profit, and it says so:

> a decile spread is a claim about a portfolio nobody has to be able to hold.

A single stock cannot be shorted in A-shares. This prerreg therefore asks the only question
that matters for money: **is the takeable, long-only part of that spread worth doing?**

## 2. Construct (frozen; changing any line changes the experiment)

Panel, CGO, ranking and cost constant are the probe's, imported:
`data/astock_daily/per/*.csv` (qfq, forward-accumulated), 60-bar turnover-attenuated cost
basis, `CGO_t = (close_t − RP_t)/close_t`, cost `COST_X1_RATE = 0.0013041` per side.

Liquidity filter (new here, frozen): a name is a candidate on date `d` only if its **20-bar
median CNY amount ≥ 20,000,000** (`etf_composite_pf.MIN_AMT`, imported — the same number the
book uses to decide what it can buy). No leverage, no shorting, equal weights, cash earns 0.

Four arms, all non-overlapping 20-bar cohorts, entry at `open[d+1]`, exit at `close[d+20]`:

| arm | book on each rebalance date |
|---|---|
| `A1_decile` | all names in the bottom **10 %** of CGO among that date's candidates |
| `A2_n50` | the **50** lowest-CGO names (a size a desk can actually hold) |
| `B_pool` (control) | every candidate, equal weight — the pool itself |
| `C_510300` (control) | buy and hold the index ETF, same span, same cost at the ends |

Then the index-timing reading, one series, two frozen signs:

| arm | rule |
|---|---|
| `B_high` | aggregate overhang `A_t` = cross-sectional **median** CGO of that date's candidates; if `A_t` is in the top 10 % of its own trailing 252 bars → hold 510300 for the next 20 bars, else cash |
| `B_low` | same, bottom 10 % |

`B_high` is the Grinblatt–Han direction (holders deep in gain ⇒ the market keeps rising);
`B_low` is the mean-reversion reading of the same number. Both are frozen here; neither may be
dropped after the run because it lost.

`A_t` needs 252 trailing bars; every arm's first usable date is the panel's own first date with
a finite CGO (rows `t < 60` are NaN by construction, so nothing is back-filled).

## 3. Costs

`cost = sum_j |Δw_j| · COST_X1_RATE` on each rebalance (a full replacement is therefore charged
two sides), and the same flat charge at the final liquidation so no arm keeps a free exit.

Cost model honesty: 13.041 bp/side is the constant the **ETF** book cards pay. A-share stock
round trips are typically 25 bp+. Every arm is also printed at **x3** cost; an arm whose excess
does not survive x3 will not be presented as a money candidate no matter how x1 looks.

## 4. Phases (a single decision sequence is not a rule)

Four decision grids = the 20-bar schedule started at offsets 0/5/10/15 bars. Every arm is run
on all four; a reading that lives on one grid only is reported as a phase accident (E188).

## 5. Criterion (frozen, no tuning after the run)

`A1`/`A2` are **ADMITTED** iff, versus `B_pool` on the same grid and the same costs:

1. full-span net excess ≥ **+1.00 pp/yr** at x1, **and**
2. the same excess stays **> 0** at x3, **and**
3. it is positive on **≥3 of 4** decision grids.

`B_high`/`B_low` are **ADMITTED** iff, versus buy-and-hold 510300 over the same span:

1. net excess ≥ **+1.00 pp/yr** at x1 and > 0 at x3,
2. beats a 200-draw circular-phase null at **p < 0.05**,
3. positive on ≥3 of 4 grids.

Anything else is `REFUSE_AS_CANDIDATE` with the failing criteria named one by one. A negative
result is the deliverable: it closes the berth and stops the next round from spending on it.

## 6. Known limits (printed with the reading, not softened)

- qfq prices near corporate actions distort "price versus cost basis"; the construct reads a
  corporate action as a jump in every holder's gain.
- float-share turnover is not the turnover of the marginal holder.
- the panel is today's listed names (survivorship); 2020-01 is the archive's own start, so the
  first usable date is 2020-04.
- a 10 % decile of ~4,800 names is not a portfolio; `A2_n50` exists precisely because of that,
  and a 50-name equal-weight book has its own concentration risk that this test does not price.