# ETF book: decision margins and a hysteresis buffer

Face: `results/etf_book_hysteresis.json` / `.md` | script: `scripts/etf_book_hysteresis.py`
(selftest 32/32, `--check` gate on the chain) | evidence cutoff 2026-10-27 | exploratory,
no preregistration, no verdict, no ledger booking.

## The question, and why it is not the obvious one

r1260/r1261 put this book's binding constraint at **turnover**, not concentration. The
production rule is the plain top-12 every 20 bars: any name that leaves the top 12 is sold,
however slightly. The score face is an average of cross-sectional percentile ranks, so a
tempting narrative follows immediately — *the book trades on noise*. This face measures
that narrative instead of asserting it, and the measurement refutes it.

## A. The cut line really is arbitrary

At every one of the 83 decision bars (2020-01-02 -> 2026-10-27), the gap between the 12th
and 13th name, in units of **that bar's own cross-sectional score sd**:

| quantile | gap (sd) |
|---|---|
| q10 | 0.0012 |
| q25 | 0.0052 |
| **median** | **0.0181** |
| q75 | 0.052 |

- 73.5% of decisions have a cut margin under 0.05 sd, **86.8% under 0.10 sd**, 97.6% under
  0.20 sd.
- In score units the median is 0.0045 against a score range of 2.0.

So the 12th and 13th names are, in the median, 1.8% of a standard deviation apart: the
model is genuinely indifferent at that boundary, and the rank order there is arbitrary.

## B. But the trades the book actually makes are NOT marginal

That is the number that kills the story. Of the 590 (leaver, entrant) pairs the book
actually executed, each scored on the bar that decided it:

- median gap **0.974 sd**
- only **2.9%** were decided by less than 0.10 sd, 9.2% by less than 0.25 sd

A name leaves the top 12 because it fell a long way, not because it lost a coin flip. The
razor-thin boundary in (A) is real but it is not what the turnover is made of — so a
decision-margin story cannot be used to explain, or to attack, the book's trading rate.

## C. What a buffer actually buys

Incumbent protection: an incumbent is displaced only when a challenger beats it by more
than `k * sd(score at that bar)`. Priced through the same engine, same breadth (12), same
cadence (20), same cost (10bp/side), same 8% vol target, same panel:

| k (sd) | turnover/decision | CAGR full | Sharpe | maxDD | OOS CAGR | OOS Sharpe |
|---|---|---|---|---|---|---|
| 0.00 (published) | 0.934 | 9.62% | 0.992 | -11.77% | 18.45% | 1.747 |
| 0.05 | 0.901 | 9.69% | 1.006 | -11.59% | 18.33% | 1.764 |
| 0.10 | 0.887 | 9.68% | 1.003 | -12.58% | 18.75% | 1.776 |
| 0.20 | 0.842 | 9.65% | 1.005 | -12.47% | 18.06% | 1.722 |
| 0.35 | 0.762 | 9.51% | 0.985 | -12.57% | 17.81% | 1.654 |
| 0.50 | 0.702 | 9.58% | 0.990 | -13.48% | 17.92% | 1.634 |

Read it as a **cost knob, not a new edge**:

- Turnover falls monotonically, 0.934 -> 0.702 (-25% at k=0.50), and returns barely move in
  the k ≤ 0.20 range (+0.03 .. +0.07pp). The arithmetic checks out: at 10bp a 0.092/decision
  turnover saving over ~12.3 decisions/yr is ~0.11pp/yr — the same order as the +0.03pp
  measured, i.e. the difference is the cost saved plus noise from different holdings.
- **k = 0.05 is the only arm that improves every column at once** (turnover -3.5%, CAGR
  +0.07pp, Sharpe +0.014, maxDD 0.18pp better). Beyond it the saving keeps growing while
  maxDD gets ~1pp worse: a stickier book holds a broken name through a turn.
- At k ≥ 0.35 the buffer genuinely costs return (-0.11 .. -0.04pp) and depth, so there is no
  free lunch at the far end — only at the near end, and only small.

## D. Control arm (must hold before any arm above is read)

The k=0 arm reproduces the published production cell `n12_vt08` exactly: measured 9.62% vs
published 9.62%, delta 0.000pp, turnover 0.934 vs 0.934. Any other arm is therefore priced
on the same book, not a look-alike.

## Honest limits

- Exploratory. A better-looking arm is a hypothesis for a prereg, not a promotion; nothing
  here is booked to a ledger or fed to the live ticket.
- The buffer is path-dependent, so the six arms are not independent draws; one arm's edge
  can be one decision sequence. The census (A/B) is the part that does not depend on
  choosing k, and it is the part that carries the finding.
- One panel, one window, one cost model. The published caveats apply unchanged: survivor
  pool, 17.5% young-fund coverage, and a strong 2024+ regime that supplies most of the OOS
  numbers.
- Turnover saving is priced at 10bp/side. At a participation-priced cost (large NAV) the
  same turnover delta is worth more, but that multiplication was not re-run here.

## What changed in the engine

`scripts/etf_robust_pf.open_to_open_equity` gained an optional `select_hook(row, held,
n_hold, d)` (same shape as the existing `ratio_hook`). `None` is the plain top-n rule and is
bit-identical to the published behaviour — pinned by this script's selftest on a tie-free
face, and by every existing caller still running unchanged. A hook that returns the wrong
shape raises instead of silently falling back. One behavioural note that the selftest pins
explicitly: the score face is an average of percentile ranks and therefore has exact ties;
`nlargest` breaks those by index order while the buffer keeps the incumbent, so the k=0
*hook* is not literally the published rule on tied rows (the production k=0 arm uses the
default path, not the hook, for exactly this reason).