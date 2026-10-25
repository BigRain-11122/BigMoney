# A-share composite factor portfolio — does the ETF construction carry over to stocks?

- date: 2026-10-25 (r1242, bm-c; script authored by the dead pre-r1242 window, this
  window fixed the sub-window metric basis, re-derived and froze the verdict)
- code: `scripts/stock_composite_pf.py`
- product: `results/stock_composite_pf.json`
- status: **exploratory measurement, zero marks, zero admission** (no paper account,
  no preregistration, no fleet lane claimed).

## Question

The ETF composite (see `ETF_COMPOSITE_FACTOR_PF.md`) earned its keep after construction
and costs. Stocks are the harder test: 20bp per side, stamp duty on sells, a much larger
cross-section, a much larger dispersion of names. Does the same construction survive?

## Setup (frozen in code)

| item | value |
|---|---|
| panel | `Money0923/data/daily/*.csv`, non-ETF symbols with >=300 bars → **164 stocks** |
| panel span | 2001-09-03 .. **2026-09-22** (evidence cutoff) |
| liquidity screen | 20d median (close*volume) >= 50M CNY, >=250 bars of history |
| factors | 28 raw factors from `engine.factors.compute_all` |
| signs | from in-sample rank IC (h=20) on 2020-2023, sign = sign(mean IC), no magnitude fitting |
| composite | cross-sectional rank-score in [-1,1], equal weight across all signed factors |
| book | top-20 equal weight, rebalance every 10 or 20 bars, start 2020-01-01 |
| cost | 20bp per side x turnover (commission + 5bp stamp on sell + slippage) |
| execution basis | signal at close of t, book set at that close, close-to-close returns |

## Results (results/stock_composite_pf.json)

Windows are renormalised to each slice's own first level (`start_level` per row).

| book | window | start level | total | CAGR | vol | Sharpe | maxDD | turns/rebal |
|---|---|---|---|---|---|---|---|---|
| composite R20 | full | 1.000 | +87.5% | 9.81% | 19.8% | 0.59 | -28.9% | 1.62 |
| composite R20 | 2020-2023 | 1.000 | +22.7% | 5.25% | 19.6% | 0.37 | -28.9% | 1.62 |
| composite R20 | 2024+ | 1.225 | +53.0% | 16.94% | 20.1% | 0.91 | -26.3% | 1.62 |
| composite R10 | full | 1.000 | +51.0% | 6.32% | 20.0% | 0.42 | -29.8% | 1.21 |
| EW universe | full | 1.003 | **+196.3%** | **17.55%** | 19.3% | **0.97** | -24.8% | — |
| EW universe | 2020-2023 | 1.003 | +54.3% | 11.48% | 19.5% | 0.68 | -24.8% | — |
| EW universe | 2024+ | 1.543 | **+92.6%** | **27.25%** | 19.0% | **1.41** | -12.7% | — |
| CSI300 | full | 1.000 | +9.5% | 1.35% | 18.9% | 0.17 | -45.6% | — |
| CSI300 | 2024+ | 0.816 | +34.2% | 11.42% | 18.6% | 0.70 | -15.7% | — |

Yearly composite R20: 2020 +27.9% / 2021 +0.6% / 2022 +1.9% / 2023 -4.3% /
2024 +51.5% / 2025 +17.2% / 2026 YTD -14.4%.

## Verdict: the ETF result does NOT carry over to stocks

This is a **negative result and it is the headline**, not a footnote.

1. The book loses to the equal-weight universe of its own eligible names on both windows
   (full 9.8% vs 17.6% CAGR; 2020-2023 5.3% vs 11.5%; 2024+ 16.9% vs 27.3%).
2. It takes more risk to lose: full-window maxDD -28.9% vs -24.8%, and the 2024+
   drawdown is -26.3% vs -12.7% — the concentration buys nothing.
3. Cost is not the explanation either. R20 turns 1.62 per rebalance x 20bp ≈ 32bp per
   rebalance, ~12.6 rebalances/yr ≈ 4.1%/yr of drag; adding that back still leaves the
   book behind the universe. The gross selection is the problem, not the friction.
4. In-sample ICs are noise-level: the best |IC| is `return_skew` at -0.052 (IR -0.38),
   and most factors sit at |IC| 0.01-0.04 with |IR| < 0.2 over 970 dates. Signing 28
   such factors and equal-weighting them adds 28 small noisy signals into one small
   noisy signal.

## Why the ETF and stock answers differ (working hypothesis, untested)

- **Panel width.** The ETF run ranked ~1,650 instruments per date; this run ranks 164.
  A 20-name top decile out of 164 is a 1-in-8 pick — the top-book is not selective and
  its dispersion is dominated by idiosyncratic single-name risk.
- **Panel depth is a slice, not the market.** `Money0923/data/daily` on this box carries
  164 non-ETF stocks only (the full A-share lane is bm-b's `update_astock_daily`). Any
  conclusion here is about 164 names, not about A-shares.
- **Sign flips are regime:** `mom_20` and `mom_60` come in negative (short-term reversal)
  while `mom_12_1` is positive, i.e. the sign table is itself a statement about one
  regime (2020-2023) that the 2024+ window may not share.

## Caveats (load-bearing)

1. **Survivorship and selection** in the on-disk panel; names that died are absent.
2. **Close-to-close basis** — no open fill, the overnight gap is neither charged nor
   credited, entry slippage unmodelled.
3. **Stale panel.** The cutoff is 2026-09-22 (no in-chain refresh leg feeds
   `Money0923/data/daily`); the live pick list is a month old and is a diagnostic, not
   a signal to trade.
4. **Not actual liquidity.** A 50M CNY median-turnover floor is a screen, not a fill.
5. **Comparisons mix two effects.** The book is 20 names, the control is ~164; the gap
   therefore combines selection and diversification. The honest statement is: *this
   selection did not pay for the diversification it gave up.*
6. **Exploratory only.** No prereg, no marks, no exit axis declared.

## Next step (pointer, not a promise)

The cheap falsifier is width, not cleverness: re-run the identical construction on the
full A-share panel once bm-b's `update_astock_daily` covers the ~5,200-name universe with
a fresh cutoff. If the book still loses to its own equal-weight control at 5,000 names,
the composite idea is dead for stocks and should be closed rather than tuned.