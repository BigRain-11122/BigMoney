# Does a top-decile premium cost anything? (r1500, bm-c)

`results/etf_premium/PREMIUM-FORWARD.json` — producer: `scripts/etf_book_premium_forward.py`
(single implementation: the panel reader is `scripts/etf_book_premium_percentile.py`).

## The question the sheet left open

r1497 answered "how high is today's premium" (own-history percentile). r1498 answered "is
that reading real or a NAV-stamp artifact" (persistence + lag ladder). The sheet then says,
honestly, **高分位不是卖单** — high percentile is not a sell order — because a limited fund
can stay expensive for years and this house holds no subscription-status data.

What neither ruler answers is the one thing the person placing the order needs: *if I pay a
100th-percentile premium, what did the price do afterwards in this fund's own record?* That
is measurable from the panel already on disk.

## Two rulers

* **Causal percentile** — each session ranked against the sessions *before* it (≥60 priors).
  Ranking a session inside its own full sample would let the future label the past.
* **Outcome = the price**, close[t+h]/close[t]−1, h ∈ {5, 20}. Not the NAV: a premium that
  "reverts" because the NAV caught up is not a loss to somebody holding the price.

Buckets: BOTTOM <10, LOW 10–30, MID 30–70, UPPER 70–90, TOP ≥90. The t-stat is computed on
**non-overlapping** samples (stride h) — h overlapping windows repeat the same move h times
and would inflate it; the overlapping count is reported only as coverage.

## Reading (panel cutoff 2026-11-09, ticket 2026-11-09, 5 legs)

Pooled rank IC of the percentile with the next 20 sessions: **−0.133** (5 legs); at 5
sessions: −0.050.

| leg | today's percentile | bucket | next 20 sessions after that bucket | n | t | on this ticket's amount |
|---|---|---|---|---|---|---|
| 159501 | 99.9 | TOP | +0.49% | 282 | +1.6 | +￥382 |
| 513100 | 98.9 | TOP | −0.22% | 295 | −0.5 | −￥175 |
| 159577 | 98.9 | TOP | −0.95% | 124 | −2.6 | −￥749 |
| 513690 | 50.5 | MID | +0.12% | 171 | +0.3 | +￥394 |
| 159263 | 16.7 | LOW | −0.64% | 32 | +4.2 | −￥505 |

Verdict **MIXED** — derived, not typed: one leg prints a real penalty (159577, t=−2.6), the
leg paying the largest premium today prints none (159501, t=+1.6), so the sign is not the
same across the book.

## What this changes for the operator

Nothing in the sizing rule: this face is a description of these funds' own records, not a
forecast, and not a cross-sectional study. What it removes is the unspoken assumption behind
"don't chase premium" — on this ticket the three TOP-decile legs have, on their own history,
a combined 20-session drift of about **−￥542 on ￥235,616**, with the sign spread across
legs. Nobody should read that as a reason to drop 159577 or to add 159501.

## Guards

`check` re-derives every bucket mean/t, the pooled IC and the verdict word from
`premium_history.csv`, and asserts the money column is *priced* (a percent-only face fails:
r1499's leg examined zero symbols and passed). Falsified four ways: a bucket mean edited in
the published JSON, the verdict word hand-typed, the ticket absent (no CNY), and the
percentile made non-causal — the first three turn `check` red, the fourth breaks selftest
L8.