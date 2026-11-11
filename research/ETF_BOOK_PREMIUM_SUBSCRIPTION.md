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

## Where it lives

* script `scripts/etf_book_premium_subscription.py` (`run` / `check` / `selftest` 19/19)
* face `results/etf_premium/PREMIUM-SUBSCRIPTION.json` + `.md`
* status cache `data/etf_premium/subscription/<code>.csv` (regenerable, gitignored)
* chain leg `premium_subscription` (check-only, ~0.2s)
