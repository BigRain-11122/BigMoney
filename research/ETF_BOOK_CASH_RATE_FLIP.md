# The cash rate at which the book's ADMIT dies

`etf_book_idle_cash` says the idle sleeve is worth paying: 0.58pp of CAGR, Sharpe 1.082 -> 1.134, drawdown slightly better, verdict ADMIT. This face asks the next question -- how far is that verdict from falling over -- because the block board carries a RED row saying the repo panel is days behind, and a reader cannot otherwise tell a disclosure problem from a verdict problem.

## What it says

<!-- FLIP-BEGIN -->
_generated 2026-11-25T03:10:12 · evidence cutoff 2026-11-24 · 1669 bars over 2020-01-03..2026-11-24_

| cash rate %/yr | gain pp | Sharpe | maxDD % | verdict |
|---|---|---|---|---|
| 0.00 | +0.00 | 1.096 | -10.56 | REJECT |
| 0.44 | +0.14 | 1.109 | -10.53 | REJECT |
| 0.89 | +0.29 | 1.122 | -10.51 | REJECT |
| 1.33 | +0.43 | 1.135 | -10.49 | ADMIT |
| 1.77 | +0.58 | 1.148 | -10.47 | ADMIT |
| 2.21 | +0.72 | 1.161 | -10.45 | ADMIT |
| 2.66 | +0.87 | 1.174 | -10.43 | ADMIT |
| 3.54 | +1.16 | 1.199 | -10.38 | ADMIT |

- flip rate (C2 target 0.30pp): **0.917%/yr** -- today's vehicle is 1.77%/yr, i.e. **85bp of headroom**
- binding gate when it breaks: **C2_cagr_gain_pp**
- a 5-day gap in the repo panel can move annual return by **0.600bp per 100bp** of rate error -- 60.04 CNY/yr per million
- the panel's last bar is **2026-11-20**; **2** book bar(s) after it accrue exactly zero (2026-11-23, 2026-11-24), so the published curve already under-pays **22.12 CNY per million** on them
<!-- FLIP-END -->
## What this is not

- not a forecast of the cash rate; the flip is a property of the gate
- not a new backtest: every grid point recomposes the same engine book
- not a replacement for the collector: the missing days still have to be backfilled, this face only bounds what they can move

Reproduce: `python scripts/etf_book_cash_rate_flip.py` (writes this block), `--check` (re-derive and compare), `--selftest` (offline legs).
