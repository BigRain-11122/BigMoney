# DIGEST 2026-11-10 r1500 bm-c — premium forward: does a top-decile premium cost anything?

**Product**: `results/etf_premium/PREMIUM-FORWARD.json` (producer
`scripts/etf_book_premium_forward.py`), S6 leg `premium_forward`, two smoke legs, card E508.

**Gap closed**: r1497 said *how high*, r1498 said *is it real*, and the sheet then printed
"高分位不是卖单" — an honest disclaimer that left the operator's actual question unanswered:
what did the price do after a fund sat in this bucket of its own record?

**Answer (panel/ticket 2026-11-09, 5 legs)**: 20-session rank IC of the causal premium
percentile = −0.133; 159577 after its top decile averages −0.95% (n=124, t=−2.6) while
159501 — today's largest premium — averages +0.49% (n=282, t=+1.6). Verdict **MIXED**,
derived from the leg table; three TOP-decile legs sum to about −￥542 of historical drift on
￥235,616 of ticket money.

**Three traps found while building it**:

1. The ticket's rows are at `ticket.order` (a list with `amount`), not `order.legs` — a naive
   read produced a percent-only face, i.e. a second copy of the two rulers it was meant to
   go beyond. `check` now fails if zero legs carry a CNY reading.
2. Ranking a session inside its own full sample would label the past with the future; the
   percentile is strictly prior-only and selftest L8 pins the direction (a low value after
   high priors must read 0, not 50+).
3. Overlapping forward windows repeat one move h times; the t-stat is taken on stride-h
   samples and the overlapping count is reported only as coverage.