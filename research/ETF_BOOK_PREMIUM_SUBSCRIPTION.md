# The premium question, answered where the data actually lives — r1546

## The question

The live book pays ~9% over its funds' own disclosed baskets; three cross-border legs sat
at the 99th percentile of their own premium history (r1497). "Why is it 20%?" was parked
because r1498 checked `data/etf_premium/nav_history/*.csv`, found `date,nav` and nothing
else, and concluded there is no subscription-status column.

**That conclusion was true of the cache and false of the source.** EM's
`fund_etf_fund_info_em` returns six columns — `净值日期, 单位净值, 累计净值, 日增长率,
申购状态, 赎回状态` — and `etf_book_premium_percentile.load_nav` reads two of them and
drops the rest. The status column has always been there; nothing in the repo kept it.

## What the column says (2026-11-11, all five legs of the published ticket)

| leg | coverage rows | 场内买入 | 暂停申购 | other words | latest stamp |
|---|---|---|---|---|---|
| 159501 | 831 | 802 | 29 | none | 场内买入 |
| 513100 | 933 | 452 | 481 | none | 暂停申购 |
| 513690 | 934 | 898 | 36 | none | 场内买入 |
| 159577 | 662 | 604 | 58 | none | 场内买入 |
| 159263 | 330 | 330 | 0 | none | 场内买入 |

Two words only, and neither of them is an open primary channel: 场内买入 means the fund is
traded on the exchange only (no OTC primary subscription listed on that day), 暂停申购 is a
hard suspension. **No session in any of the five histories shows an open primary
subscription.**

## The readings

1. **Channel census** (`window_verdict`): 5/5 legs CHANNEL_CLOSED_THROUGHOUT. The valve an
   arbitrageur needs to compress a premium was not listed as open on any session this face
   can see. This is a mechanism statement, not a valuation one.
2. **Within-leg contrast** (`block_contrast`) — the only place the data has a difference:
   513100 spends 679 sessions hard-suspended with a median premium of +5.04% against +0.54%
   while exchange-only (**+4.50pp**, BLOCK_WIDENS_PREMIUM). 159501 (+0.22pp) and 159577
   (−0.60pp) come out flat or negative — the hard block does **not** widen their premium.
3. **High-premium sessions** (≥10%): 159501 82 sessions, 513100 163, 159577 2, and all of
   them closed-channel. On a leg with zero suspended sessions (159263) that share reads
   100% by construction, so the column is a census, not a contrast — stated on the page.

## Days are not runs (r1547)

Reading 2 counted **days**, and a day count is not a sample size. Once the runs are named
(`episode_granularity`), the 830 hard-suspended sessions across the five legs turn out to be
**141 runs, 116 of them a single NAV row** — i.e. one word printed between two exchange-only
rows, which is a blip rather than a policy. And on 513100, the leg that carried the whole
headline, the +4.50pp is not spread over its 48 runs:

| leg | blocked runs | one-row blips | longest run | its own gap | the other runs |
|---|---|---|---|---|---|
| 159501 | 29 | 29 | 1 session | −1.18pp | +0.49pp |
| 513100 | 48 | 43 | **435 sessions** (2024-11-26..2026-09-08) | **+4.28pp** | **+0.06pp** |
| 513690 | 42 | 24 | 3 sessions | −0.68pp | +0.20pp |
| 159577 | 22 | 20 | 30 sessions | −1.42pp | +0.42pp |

So the honest statement is narrower than r1546's: **on 513100 the block and the premium moved
together through one long suspension — one decision by one fund, n=1 — and the 43 single-row
suspensions around it show no elevation at all (+0.06pp).** A day-level median over one long
run and hundreds of correlated repeats of that same run cannot tell a policy effect from a
coincidence of timing. This is the same failure the calendar rule has (E222: one observation
per month, not per day), and it was cheap to catch only because the runs were named.

The face keeps both readings and says which one has a count behind it; `check` now refuses a
published face that prints a block count without printing whether its gap survives dropping
the widest run.

## Why this is falsifiable

The hypothesis "the premium is a 限购 artefact" dies the moment any session shows an open
primary subscription at a high premium. `check` mode refuses a published face where an open
stamp sits beside CLOSED_THROUGHOUT, and the selftest carries a fixture that puts an open
session above the line so the red path is exercised, not just described.

## What it does not say

* A closed channel is consistent with a standing premium; it does not make the premium fair
  and it is not a sell signal.
* The word is as published per NAV row; it says nothing about quotas or how much would be
  accepted on reopening.
* 513690 and 159263 price at −0.78% / −0.54%: the "20% premium" is a three-leg story
  (159501 / 513100 / 159577), not a five-leg one.

## Are the single-row runs scattered, or printed on a rhythm? (r1548)

The run table says 116 of 141 blocked runs are one NAV row. This round asked the next question
instead of leaving it as the word "blip": do those days look like ordinary sessions?

* **59 of 116 (50.9%) fall on Tuesday**, against 20.3% of all priced sessions -- one-sided
  binomial chance 2.6e-13. Peak days of the month 26 (11), 5 (8), 20 (8).
* **116 of 116 are bracketed by 场内买入 on both sides**, and only **1** carries a NAV jump above
  3% (513100 2022-01-13: 5.19 -> 1.01, a share split) -- so a split cannot explain the rest.
* Per leg only 513100 clears the line on its own (60%, 9.8e-09); 159501 / 513690 / 159577 lean the
  same way with too few runs, which is why the pooled reading is the one quoted.

What this establishes is **when** a one-day word appears, never **why**: a source that refreshes
its status column weekly and a fund that announces one-day suspensions are the same shape here.
What it settles is the reading -- a single-row run is a word printed on one session, and must not
be priced as "the fund was suspended that day".

## Where it lives

* script `scripts/etf_book_premium_subscription.py` (`run` / `check` / `selftest` 51/51)
* face `results/etf_premium/PREMIUM-SUBSCRIPTION.json` + `.md`
* status cache `data/etf_premium/subscription/<code>.csv` (regenerable, gitignored)
* chain leg `premium_subscription` (check-only, ~0.2s)
