# ETF composite book — where does the 9%/yr actually come from?

- date: 2026-10-25 (r1243 bm-c)
- code: `scripts/etf_composite_decomp.py` + `scripts/etf_asset_class.py`
- product: `results/etf_composite_decomp.json`
- upstream: `research/ETF_COMPOSITE_FACTOR_PF.md` (R20 headline 9.04%/yr full, 15.30% 2024+)
- status: **exploratory measurement, zero marks, zero admission.**

## Question

The published R20 book holds bond ETFs on most days. That leaves the honest question
open: is the edge cross-sectional *equity* selection, or simply "be long bonds/gold when
equity momentum is bad"? This decomposes the book by asset class and re-runs the same
score with the non-equity ETFs removed from the universe.

## Setup

Same panel, same factors, same signs, same cost model as the published module (imported,
not re-implemented): top-5 equal weight, rebalance every 20 bars, 8bp per side on
turnover, close-to-close from the decision close, start 2020-01-01, cutoff 2026-10-23.
Two books differ only in the eligible universe:

| book | universe |
|---|---|
| `all_classes` | 1,653 ETFs (as published) |
| `equity_only` | 1,291 equity ETFs; bond (104), commodity (18), cross-border (238) and convertible (2) removed before ranking |

Class tags come from **names** in `data/basic/etf_list.csv` (`scripts/etf_asset_class.py`),
with a code-prefix fallback — see the pitfall section, it is load-bearing.

## Results (results/etf_composite_decomp.json)

| book | window | start level | total | CAGR | Sharpe | maxDD |
|---|---|---|---|---|---|---|
| all_classes R20 | full | 0.998 | +80.2% | **9.04%** | 0.898 | -12.8% |
| all_classes R20 | 2020-2023 | 0.998 | +21.1% | 4.92% | 0.516 | -12.8% |
| all_classes R20 | 2024+ | 1.206 | +49.1% | **15.30%** | 1.466 | -10.2% |
| equity_only R20 | full | 0.996 | +32.7% | **4.24%** | 0.375 | -26.7% |
| equity_only R20 | 2020-2023 | 0.996 | +9.0% | 2.18% | 0.232 | -20.8% |
| equity_only R20 | 2024+ | 1.090 | +21.2% | **7.11%** | 0.552 | -14.8% |
| EW all classes R20 | full | 1.001 | +17.9% | 2.44% | 0.230 | -40.0% |
| EW all classes R20 | 2024+ | 0.911 | +29.5% | 9.65% | 0.596 | -18.9% |
| EW equity R20 | full | 0.999 | +14.1% | 1.90% | 0.198 | -44.3% |
| EW equity R20 | 2024+ | 0.908 | +25.1% | 8.32% | 0.475 | -24.2% |

Every window is measured against its own first level (`start_level` recorded per row).

### Exposure and attribution (all_classes book)

| class | days held (share) | mean weight when live | arithmetic contribution |
|---|---|---|---|
| bond | 1,407 (85.4%) | 62.8% | +8.57pp |
| equity | 1,280 (77.7%) | 39.4% | +38.04pp |
| commodity (gold etc.) | 220 (13.4%) | 45.5% | +21.47pp |
| cross-border | 340 (20.6%) | 43.5% | +3.75pp |
| convertible | 46 (2.8%) | 20.0% | -0.69pp |

Average bond weight across all days: **53.6%**. Days with bond weight above half: 867 of
1,647 (52.6%). Whole-book-in-bonds rebalances: **16.9%** (the "~half the calendar in
bonds" phrasing in the upstream note overstates this specific statistic — see the
discrepancy note below; the qualitative claim stands).

## What this changes in the reading

1. **About half the headline is defensive rotation.** Remove bond/gold/cross-border and
   the full-sample CAGR falls 9.04% → 4.24% while maxDD nearly doubles (-12.8% → -26.7%).
   The score's willingness to buy bonds in bad equity regimes *is* the product, not a
   side effect.
2. **No surviving equity-selection alpha out of sample.** The equity-only book beats its
   own equal-weight control full-sample (+2.34pp/yr) but **loses** to it after 2024
   (7.11% vs 8.32%, Sharpe 0.55 vs 0.48). Whatever the ETF composite is earning lately, it
   is not cross-sectional stock/sector selection.
3. **Gold is a large, concentrated contributor.** Commodity ETFs sit in the book on 13.4%
   of days and carry +21.5pp of the arithmetic return, essentially all of it in the
   2024-2026 gold run. A book whose headline depends on one 18-name sleeve is a
   different product than "a factor portfolio".
4. **The ranking is doing regime selection, not factor selection.** Bond ETFs win the
   composite precisely when equity momentum/trend is negative — that is a defensible
   timing rule, but it should be described as one, and evaluated as one (with a
   regime-aware benchmark), not as a cross-sectional factor book.

### Permutation null on the equity-only book (200 date-wise shuffles)

Same shuffle scheme as upstream (each factor's cross-section permuted date by date,
keeping the rank distribution and the universe, destroying the factor→return link),
re-picked top-5 with the same cost model:

| statistic | value |
|---|---|
| real period-Sharpe | 0.384 |
| null mean / p95 / max | 0.108 / 0.431 / 0.582 |
| p-value (null >= real) | **0.07** (14 / 200) |

The upstream all-class book's null was p=0.000 against the same 300-shuffle scheme; the
equity-only book does not clear 5%. Read together: the significance in the published
number lives in the defensive sleeve and the shuffle destroys it once that sleeve is
removed from the eligible universe.

## Pitfall (load-bearing, caught inside this analysis)

**Code prefixes are not asset classes.** A first pass tagged classes by prefix
(511=bond, 518=gold, 513=cross-border) and left `159395/159396/551900/551510` — all
bond/money-market ETFs — in the equity bucket. Because those are exactly the names the
score buys in risk-off phases, the "equity-only" book then reported **10.03%/yr**, i.e.
*higher* than the all-class plan (9.04%) and almost exactly the opposite of the
name-based answer (4.24%). One classifier mistake flipped the conclusion. Any
asset-class split on this panel must be name/metadata based; prefix heuristics are only
a fallback and must be logged when used.

## Discrepancy disclosed, not smoothed

The upstream note says "roughly half the calendar is cash/bonds". Measured here: bond
weight above half on 52.6% of days, fully-bond rebalances 16.9%. The two statements
describe different statistics (day-level exposure vs rebalance-level book composition);
the 48%-style figure read as "rebalances" would be wrong by ~3x. Nothing upstream is
edited; this report is the correct reading.

## Caveats (unchanged from upstream + two new)

1. Close-to-close basis, no open-fill model, so entry slippage is unrepresented.
2. Survivorship in the on-disk panel (only ETFs that still exist).
3. 20M CNY median-turnover screen is a screen, not a fill; top-5 is thin capacity.
4. 2024+ is one regime; 2025 alone carries most of the excess.
5. **New:** the arithmetic contribution column is a sum of daily w·r, not a compounded
   contribution — it is a ranking device, not a decomposition identity.
6. **New:** class tagging covers 1,676 listed ETFs; names outside the list fall back to
   prefix/default equity, which can only under-remove, never over-remove.

## Next step (pointer, not a promise)

(a) re-run with a genuine next-open fill using the already-loaded `openp` panel;
(b) treat the defensive sleeve as the thesis: build the regime-timing book explicitly
    (equity sleeve vs bond sleeve by a stated rule) and prereg it under
    `TRIAL_LABOR_LAW §4` with an explicit exit axis;
(c) stress the gold dependence: equity+gold-only variant, and the same book with the
    commodity sleeve removed;
(d) survivorship-free panel (point-in-time ETF list) before any capacity claim.