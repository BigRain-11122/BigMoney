# DIGEST 2026-11-02 r1230 bm-a — depth and duration are different risks

**Round product.** `scripts/etf_book_underwater.py` (selftest 14/14, `--check` OK) — the first
face of this book that prices the **wait**, not just the fall. The card and every research face
state CAGR, Sharpe and a max drawdown point; a holder's real question ("if I start on a bad
day, how long am I under water") had never been answered anywhere in the repo.

**Live reading** (production cell `n12_vt08`, cutoff 2026-10-30, 1652 bars, control reproduced
to 0.0pp on CAGR and maxdd at tol 5e-5):

- longest underwater episode: peak 2021-09-14 → trough 2022-11-01 (−11.77%) → healed
  2023-03-02, **350 bars**
- 54 episodes, 53 healed, **1 still open on the last bar** (`recovered: false`, kept)
- worst entry = that same peak, **351 bars to get even**; median 1 bar, p90 14.9 bars
- forward calendar horizons: 1y min **−7.51%** (8.0% of entries negative), 2y min −0.02%,
  3y min **+0.78%** with **0%** of entries negative

**Why censored entries are load-bearing.** An entry whose money is still under water on the
last bar must print "still under water after N bars". Scoring it as 0 (the obvious
implementation: `min(bars if found else 0)`) makes the book look faster than it is — the same
shape as the defects this desk fixed in r1261/r1266: an empty measurement reported as a good
reading.

**Frozen before the run.** Control = the published cell, tol 5e-5, refuse-to-publish on
mismatch. Horizons are calendar years via `DateOffset`, not 252 bars/year. Verdict is
descriptive — no threshold decides whether the book is good; the only failure mode is
`CONTROL_MISMATCH`.

**Honest boundaries.** 2020-01 → 2026-10 only (the pre-2020 book is priced separately and not
pooled); nominal equity (no deflator, no funding cost on the cash leg); ETF pool = the ETFs
that exist today (survivorship, already disclosed on the card). The 3-year "no negative entry"
result is a property of a 6.8-year rising sample, not a promise.

**Files.** `scripts/etf_book_underwater.py`, `results/etf_book_underwater.json`,
`research/ETF_BOOK_UNDERWATER.md`, card E346, two smoke legs (exit-code contract + verdict
re-derived from the published rows, which also refuses a censored-as-zero implementation).