# E-face: which part of the day earns the book's CAGR (r1188 bm-a)

**One line.** The book's CAGR is not earned by trading: the 83 rebalance days are a *net
cost* (-13.2 bp each) and the 1,569 quiet bars carry the whole return (+4.2 bp each).

Producer: `scripts/etf_book_leg_attribution.py` (selftest 9/9, `--check` rc0).
Artifact: `results/etf_book_legs/LEGS-2026-10-30.json` + `latest.json`.
Chain leg: `etf_book_leg_attribution` (gate-only `--check`, run = ~20 s panel build).
Smoke leg: "product: the book's CAGR is split into overnight / intraday / quiet / toll and
the split closes to the same total" (with three doctored copies the checker must reject).

## Why this exists

Every published number for this book -- card, ticket, CEO page, dashboard, ledger -- is one
CAGR. Nothing on any face said *when* it is earned. The four candidate legs were already
inside the engine (`etf_composite_pf.run_next_open` books them explicitly):

| leg | what it is | who earns it |
|---|---|---|
| overnight | close(d-1) -> open(d) | the OLD book, while the order is still pending |
| intraday | open(d) -> close(d) | the NEW book, after the fill |
| plain | close(d-1) -> close(d) | a bar with no fill at all |
| toll | -(rate x turnover) | charged at the open of the fill bar |

So the attribution is not a new model: it is the same state machine
(`etf_book_forward.Forward`, subclassed, one function copied) with four log buckets added at
the four places that machine multiplies the nav. The four buckets sum to log(nav_final)
**exactly**, and the walker is proven to BE the engine on the run's own panel --
`engine_identity_max_abs_diff = 0.0` (not a fixture: the production arm's nav curve equals
`Forward`'s to the last bit, and `--check` refuses any face where that number is not ~0).

## Readings (panel `a1a42aee64453839`, 2020-01-02 -> 2026-10-30, 1,504 symbols, 1,653 bars)

| arm | CAGR | log pp/yr | overnight | intraday | quiet | toll | fill-bar net |
|---|---|---|---|---|---|---|---|
| **production** (12 names, 8% vol target, 10bp) | 8.49% | 8.21 | +0.16 | -0.64 | **+9.83** | -1.15 | **-13.21 bp** |
| base_book (same selection, no overlay) | 13.13% | 12.43 | +0.47 | -0.56 | +14.09 | -1.57 | -13.53 bp |
| control_ew (all 1,504 names equal weight, same grid) | 4.03% | 3.98 | -0.14 | -2.00 | +6.20 | -0.07 | -18.12 bp |
| **wedge (book - control)** | +8.45pp | | +0.61 | +1.44 | +7.89 | -1.49 | |

Per bar of the type it books on (bp):

| arm | quiet bar | fill bar: overnight | fill bar: intraday | fill bar: toll | fill bar net |
|---|---|---|---|---|---|
| production | +4.24 | +1.33 | -5.19 | -9.35 | **-13.21** |
| base_book | +6.08 | +3.83 | -4.58 | -12.78 | -13.53 |
| control_ew | +2.68 | -1.17 | -16.34 | -0.61 | -18.12 |

## What it means (and what it does not)

1. **The toll is the single most identifiable line.** 1.15 pp/yr = 14% of the book's log
   total, and on a fill bar it is 9.35 bp -- three quarters of the fill bar's total loss.
   This is the same cost the toll ladder prices ex ante; here it is priced ex post, per bar.
2. **Rebalance days are a cost centre, not an entry point.** The book pays the toll and, on
   those same days, loses on the session leg. The return comes from holding between them.
   That is not an argument for a longer grid on its own (the grid is already measured, the
   buffer arms already REJECT), but it is the reading any "should we rebalance more often"
   proposal has to beat.
3. **Selection shows up in the quiet bars too, not only in the fill.** Against an equal-weight
   book of the same 1,504-name pool on the same grid, the wedge is +8.45 pp/yr and it is
   spread across all four legs; the largest piece is the quiet bars (+7.89).
4. **The A-share "overnight negative / intraday positive" fact (E21 census, stock level) does
   NOT transfer to this pool as a session leg.** Here the *quiet* bars carry the return and
   the *fill-bar session leg* is negative for both the book and the control. The control's
   -16.3 bp intraday on grid days is large and unexplained by anything measured so far; it is
   recorded as an open question, not as a finding, because 83 bars is a small sample and the
   open prints of ETF gaps are known-imperfect (a missing open falls back to that bar's
   close, which forces that name's intraday leg to zero rather than to a wrong number).

## Honest limits

- **Carry is off.** Cash earns nothing in this walk, so a de-levered production book's cash
  fraction contributes 0. The card's carry split (E172) is a different face and is not
  re-priced here.
- **Log attribution.** pp/yr are log contributions; they add exactly to log CAGR and only
  approximately to the geometric CAGR (8.21 vs 8.49%). Both are published.
- **Survivorship** is unchanged: the pool is today's listed ETF set.
- **Bucket totals are readability traps**: 95% of the bars are quiet, so "quiet = 92% of the
  return" is arithmetic, not insight. Every bucket is therefore also published per bar of
  its own type, and `--check` refuses a face whose per-bar reading does not reproduce its
  bucket (a face whose arithmetic does not close is a caption, not a measurement).
- Zero prereg, zero judged face, zero engine edit, zero network, zero pool write.