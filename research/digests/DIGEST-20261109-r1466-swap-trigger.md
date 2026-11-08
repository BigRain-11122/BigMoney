# r1466 — the sheet that carries the swap now carries the trigger

**Question.** r1465 split today's re-tickering into CNY 1,540 repeatable and CNY 8,222 one-off.
That is a number on a page. The desk's next question is not economic, it is procedural: *I did
the swap — when does this decision have to be looked at again, and what number makes me look?*

**Answer.** Two clocks, and they are not the same clock.

- **Decision clock** — the book re-ranks every 20 sessions; on that bar the swap is re-decided
  from scratch. No special watch is needed there.
- **Gap clock** — between two decision bars the only thing that can move is the pair's gap, and
  the only reason to act again is that the toll is no longer worth paying. That is priceable:
  this book pays 8bp per side, so acting again costs a round trip of **0.16 pp** of notional.

So the trigger is the round-trip toll — not a percentile, not a historical mean.

**Perishability is measured, not asserted.** For every historical session whose gap was at least
half as wide as today's excess over its own mean, count the sessions until the gap returns to the
mean. Episodes still wide at the end of the panel are **censored and reported**, never scored as
zero sessions (r1230's "empty measurement written as a good reading").

| pair | today | mean | share above toll | episode lifetime | word |
|---|---|---|---|---|---|
| 159501 → 159513 | +8.67 pp | +0.83 pp | 63% | unmeasured (1 episode, never healed) | ACT_ON_THIS_BAR |
| 513100 → 159513 | +6.29 pp | +1.41 pp | 85% | 22 sessions (1 healed, 1 censored) | WINDOW_ALWAYS_OPEN |
| 159577 → 513850 | +0.19 pp | −0.08 pp | 39% | 3 sessions (median of 27) | NOT_ACTIONABLE |

**Three reusable rules**

1. *A word has to be executable.* "PERSISTENT / EPISODIC" describes; the person holding the sheet
   needs "do it on this bar / any bar / don't". Every word carries an action.
2. *A missing measurement resolves toward acting, not toward waiting.* For 159501 no comparable
   episode ever healed inside 793 sessions, so the lifetime is unknown — and unknown is not
   "there is time". Writing it the other way round would have the book sit still on the one day
   that mattered.
3. *An upstream refusal may not be revived downstream.* 159577's 0.19pp clears this face's own
   0.16pp toll, but the sibling face already called it GAP_IMMATERIAL; the downstream gate reads
   the upstream word first, otherwise a 146-CNY non-event becomes a trade.

**Where it lands.** `scripts/etf_book_swap_trigger.py` (selftest 20/20, `--check` CHECK_OK,
0.3s) → `results/etf_book_swap_trigger.json` + `.md`. The **executable ticket itself** now prints
the section (`scripts/etf_book_order.py::swap_trigger_md`, selftest 101→103/103), so the operator
holding `ORDER-2026-11-06.md` reads the trigger next to the weights; an absent face prints one
line ("this question cannot be answered"), never a blank section that reads as "nothing to watch".
S6 leg `swap_trigger` follows `sibling_gap`; two smoke legs; card E472.

**Caveats.** The trigger is priced in pp of notional against the round-trip cost only — no
tracking difference, fee, size or FX-hedge policy between the two tickers. Episode lengths are
measured on the reconstructed gap, which inherits the single IOPV anchor of the gap face.