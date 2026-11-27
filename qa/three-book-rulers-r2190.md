# QA — three_book_rulers (r2190, bm-c)

**Product**: `scripts/three_book_rulers.py` → `results/three_book_rulers.json` / `.md` /
`research/THREE_BOOK_RULERS.md`.

**The question it answers**: the repo now quotes three books in annual percentages
(ETF composite 9.94%, CB dual-low sleeve 6.34%, index-futures carry 10.22%). Are those
three numbers the same kind of object? If not, which one is the reader allowed to compare?

**Verdict**: `THE_SMOOTH_LINE_IS_THE_ONE_NOBODY_CAN_HOLD`.

On one window (2020-01-03..2026-11-26, 1671 bars, 244-day clock) the three print
9.94% / 6.34% / 10.22%. The carry line wins the table and cannot be bought:

| object | sharpe | what it is |
|---|---|---|
| basis only (published) | 2.9720 | basis move net of cost — no index, no hedge, no account; quoted per notional |
| excess after hedge (published) | 1.4162 | same day minus the same notional's index return — what a hedged sleeve earns |
| unhedged per-lot points (published) | 0.5057 | carries the index's own vol |
| this face's basis series on the common window | 3.1893 | the 2020-2026 slice of the same basis arm |

Capital line (published sizing rule, 8% hard cap, IC per-lot hedged vol 91,029 CNY):
one lot needs **1,137,862 CNY**; the wallet has **1,000,000**; executable lots **0**;
gap **137,862**; the book's own decision is `WITHDRAW_FROM_TICKET`.

Capital-return identity printed beside it: 8.0% × 1.4162 = **11.33%** for the hedged arm,
8.0% × 2.9720 = **23.78%** for the basis arm (the arithmetic a reader runs if they take the
page's Sharpe at face value). It is an identity for a vol-targeted book, not a forecast, and
the face says so.

## Evidence

- selftest **18/18** (`python scripts\three_book_rulers.py --selftest`).
- `--check` → `{"ok": true, "kind": "CHECK OK", "detail": "CHECK OK (3 books, cutoff 2026-11-26)"}`.
- Independent recomputations inside the selftest: carry total return against the compounded
  plan returns (±1e-6); ETF vol against a separately built ratio chain; window start/end against
  `max(firsts)`/`min(lasts)`; lots recomputed from the published rule at both the wallet and the
  first rung; the gap identity.
- Drift behaviour legs: a mutated verdict → `CHECK FAILED` **without** the word STALE (so the
  chain does not pay for a rewrite on a real defect); a moved input sha → `STALE` (so it does).
- Negative controls: basis arm stops winning → verdict changes; wallet funded to one lot →
  verdict stops claiming unreachable; hedged arm keeps the basis Sharpe → verdict stops
  claiming a gap.

## Self-catches this round (all found by running, not by reading)

1. **Level books were not rebased.** `_nav_level` returned the parent's own level (CB starts at
   2.596 in 2020 because its series begins 2007), so `cagr = final_level ** (1/years) - 1`
   printed CB at **22.25% cagr / +295.5% total** — obviously impossible next to its own
   yearly table. The selftest leg "carry total return equals compounded daily plan returns"
   and the by-year block are what surfaced it. Fixed by rebasing every level series to 1 at the
   window start.
2. **`check()` looked for the face in the repo root** (`FACE + ".json"`) instead of
   `results/`. Caught immediately by the selftest's own `check is green on a freshly built face`
   leg rather than by a false green.
3. **Three selftest expectations were wrong, not the face**: the carry total compared against a
   product that still included the window's first row; the ETF vol compared an unrounded value
   against the face's 4-dp stored value; and the third negative control moved the published
   basis Sharpe (2.972) where the verdict reads the same-window recomputation (3.189), so the
   control was not controlling the branch it claimed to.

## What this face does not do

- It re-prices nothing, re-runs no backtest rule, and relabels no published number.
- It does not put carry on a window that starts earlier than 2020-01-03 (IC has bars from
  2017, the other two books do not); it refuses that window on purpose and says why.
- It does not measure the hedging cost itself — it reads the family's published hedged arm.
- It does not fix the standing gap that the three books' costs, universes and turnover differ;
  it only aligns dates and clocks.

## Standing debt still open (unchanged by this round, contention window)

Chain leg, smoke leg and a CEO-page sentence for the r2183/r2186/r2187/r2188/r2189/r2190 family
are still blocked on shared faces (`repo_write_contention` rc=3 CONTENTION this round:
3 hosts, 23 peer-written shared faces). Seventh consecutive round for this debt.
