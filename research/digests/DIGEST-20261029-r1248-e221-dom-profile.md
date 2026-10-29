# E221 — the month boundary is a session story, and a calendar effect's sample size is months

Round 1248, bm-b. Runner `scripts/e221_dom_profile.py`, face
`results/dom_profile/PROFILE-20261028.json`, card E221.

## Why this exists

E61/E215/E218/E219/E220 spent five cards on one question — does rebalancing mid-month
cost you anything — and closed with *no quotable number at any width*: on a ten-name
book the control's own draw noise was 20-50x the 18bp it was meant to explain.

That left an unasked, much cheaper question underneath it: **is the month boundary a
special place for ETF returns at all?** A five-name book cannot answer it, but the
in-repo panel can: 1,725 ETFs x 5,268 sessions.

## What was measured

Close-to-close equal-weight cross-section per session, bucketed by session position in
the month (counted from both ends, on the session calendar — not on calendar days).
Standard errors are computed over **sessions**, not over name-days.

| group | sessions | mean bp | t |
|---|---|---|---|
| unconditional | 3,786 | +2.20 | 1.18 |
| month-end (last 2 sessions) | 376 | +8.31 | 1.35 |
| last session only | 188 | **+19.20** | 2.13 |
| penultimate session only | 188 | -2.58 | -0.31 |
| mid-month (sessions 6-15) | 1,869 | -0.47 | -0.18 |
| rest of month | 1,569 | +3.91 | 1.31 |
| first session of month | 187 | **+27.47** | 2.69 |
| turn-of-month (last + first) | 375 | **+23.32** | 3.43 |

Month-end minus rest = **+4.40bp, SE 6.84, t=0.64** — not resolvable.

## The load-bearing reading

Two numbers carry the card.

1. **The mass sits on the turn of the month, not on "month-end".** The last-two-session
   average (+8.3bp) hides a +19.2bp last session and a -2.6bp penultimate one. "Month-end
   premium" as a two-day bucket is the wrong shape; the two boundary sessions are.
2. **Widening the cross-section buys no power for a calendar effect.** 1,725 names do not
   make the month boundary 1,725 times more measurable: the independent observation is
   the month. There are 188 usable month-ends in this panel, so the power block says a
   4.40bp gap at 80% power needs **3,567 months — about 297 years**. The E219 conclusion
   ("no quotable number at any width") is therefore not a defect of the ten-name book; it
   is a property of calendar questions on a 14-year panel.

The best single cell in the 23-bucket ladder is the last session (+19.20bp, t=2.13), and
the ladder's own multiple-comparison bar is 3.07 — it does **not** clear it. The
turn-of-month group (t=3.43) does clear that bar, but it was formed *after* seeing the
ladder, so it is a candidate for a pre-registered test, not a finding. Both caveats sit
in the face (`best_bucket.clears_bonferroni=false`, `power.turn_of_month_adjacency`).

## Products

- `scripts/e221_dom_profile.py` — runner + 18 hermetic selftest legs (fixtures: a
  +100bp month-end fixture, an opposite-sign two-month fixture, thin sessions, a missing
  print, determinism, and the multiple-comparison bar).
- `results/dom_profile/PROFILE-20261028.json` + `by_dom.csv`.
- S6 leg `dom_profile` (after `sharedbookwidthsplit`, before the CEO pages).
- Smoke leg: recomputes the published gap from the published group stats and fails if
  the power block, the multiple-comparison bar, or the coverage count goes missing.

## Pits caught in-window

- `if me["se_bp"] and rest["se_bp"]` reported *insufficient days* for a perfectly
  measured 100bp gap, because a zero-variance group has `se == 0.0` (falsy). Test
  against `None`. The first selftest run caught it.
- Two of my first selftest legs were wrong, not the code: the fixture's month-end
  sessions are all identical so their session sd is 0. The replacement fixture moves
  every name identically each session (+100bp in one month, -100bp in the next), which
  is exactly the case where a **name-day** standard error would print 0 and call a
  cancel-to-zero mean infinitely significant.

## Honest faces

Descriptive census only: no gate, no verdict, no prereg, no trial count consumed. No
costs and no execution model — this is a return profile, not a tradable rule. The ETF
universe is today's listed set (listing survivorship). A stale close (an illiquid ETF
repeating yesterday's print) enters as a 0bp return; before 2013 fewer than 20 names
print in a session, so 1,481 early sessions are dropped rather than averaged.