# ETF book -- hindsight signs or textbook signs?

_generated 2026-11-22T18:58:32+08:00 | evidence cutoff 2026-11-20 | source face results/etf_sign_stability.json (64 arms, digest 39ced71beca0)_

## The question

E207 measured that the six production directions in `etf_composite_pf.SIGNS` are the full-sample IC signs, and `etf_sign_pit` judged that `signs_in_sample`. Both are true. But each of the six directions also follows from the factor's own definition -- so the sign set may be hindsight and textbook at the same time, and the only question that can change a decision is which one it actually is, and whether peeking paid.

## What each direction is, before any data

| factor | prior sign | why (from engine/factors.py) |
|---|---|---|
| `mom_12_1` | + | 12-1 month momentum, the academic classic -- past winners keep winning |
| `price_position` | + | close near the top of its N-day range -- breakout strength |
| `drawdown_60` | + | close near its 60-day high (value is <= 0) -- relative strength |
| `adx_14` | + | trend strength -- a trending name is the one a trend basket wants |
| `vol_60` | - | realized vol -- low vol is the defensive tilt this book is built on |
| `intraday_range` | - | intraday range -- noisy intraday chop is what a daily book does not want |

The textbook key `mom_12_1+|price_position+|drawdown_60+|adx_14+|vol_60-|intraday_range-`

- the face this book actually trades: `mom_12_1+|price_position+|drawdown_60+|adx_14+|vol_60-|intraday_range-`

- same object? **yes**

## What peeking pays, versus the textbook

| arm | IS cagr (rank) | OOS cagr (rank) |
|---|---|---|
| **textbook / production** | +2.12% (8/64) | +12.27% (9/64) |
| in-sample best (what peeking picks) | +4.81% (1/64) | -8.49% (50/64) |
| out-of-sample best (hindsight only) | -4.89% (37/64) | +31.05% (1/64) |
| every prior flipped | -5.38% (39/64) | +1.64% (29/64) |
| median of all 64 (no information) | -4.27% | +0.17% |

Prior arm top-quartile in **both** halves: **yes** (shared set size 7 of 64). 34 of 64 arms earn a positive OOS cagr -- the panel itself was kind, which is why the comparison is against the median arm and not against zero.

## Verdict

**`peeking_loses_to_the_textbook`**

Reading: the production sign set is the textbook sign set. Peeking at the panel picks the in-sample-best arm, and that arm's out-of-sample number is -8.49% against a median arm of +0.17% -- so on this panel hindsight was not merely unnecessary, it was worse. The `signs_in_sample` flag on this book therefore records a **fact about how the config was written**, not a hidden premium in the published return.

## Caveats

- Sub-period numbers come from the same trading path as the full-window arm (no fresh flat start at the split), the inherited caveat of `etf_sign_stability`.

- Reference engine, flat sizing (no vol target / beta overlay): this is a sign-choice question, not the card's headline.

- The six prior directions are asserted from the factor docstrings, not derived. A reader who disagrees with one of them must move that one sign and re-read the table; the reverse-prior row shows the cost of being wrong about all six at once.

- ETF pool is today's listed set (survivorship), unchanged on this line.
