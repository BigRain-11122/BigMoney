# E138 — the panel that never refreshed, and the session the vendor publishes tomorrow

*round r1289 · 2026-10-26 evening · bm-c*

## What was broken (three defects, one of them a week old)

1. **The wide ETF panel had no refresh leg at all.** `scripts/update_etf_wide.py`
   was written and committed in r1257, ran once by hand, and was never added to
   any chain. Nothing referenced it: `Tools/s6_chain_bmc.py` listed
   `update_daily` and `update_etf_daily` (the five-member face) but not the wide
   leg. So the 1,724-file panel that is the price universe of every ETF study
   **and of the production book** was frozen at whatever r1257 pulled, and every
   downstream face (card, ticket, forward ledger, regime, thermo) kept computing
   on it. This is the same failure shape as r1107's marks lane: airtight on the
   script side, absent on the schedule side.

2. **The wide leg wrote its status into the five-member lane's status file.**
   It imported `scripts.update_etf_daily as U` for its helpers and called
   `U.write_status(payload)` — but `U.STATUS` is
   `results/etf_daily_pull_status.json`, the five-member lane's own face. For a
   week that file described the wide panel (`universe: 1724`, `quote_topup_*`)
   instead of the five members, so the lane that is frozen research face had no
   readable status. Now each lane writes its own file
   (`results/etf_wide_update_status.json`) and a selftest leg pins the paths
   apart.

3. **A one-session vendor lag delisted the universe.** The ended-source rule was
   `src_last < expected -> source_ended`, and `panel_cutoff` excludes ended
   stems. On any day the vendor publishes late, *every* symbol is "ended", the
   excluded set becomes the whole universe, and the freshness gate reports
   clean while the panel is a day stale. "Source ended" is now a trading-day
   distance (`>= 5` trading days of silence), computed from the **official**
   calendar — the panel's own tail cannot answer "is today a trading day" while
   the panel is the thing that is behind (E136's self-referential calendar,
   second instance).

## The same-evening gap, and how it is closed

`klc_kl.js` (the history face used by every refresh leg) publishes a session
only the next morning: at 19:29 on 2026-10-26 it still ended at 2026-10-23,
while the exchange had closed five hours earlier. So even a wired panel could
not carry tonight's close until tomorrow, which is exactly what blocked the
r1264 milestone ("first real forward mark off the 2026-10-26 close") for four
rounds.

The same vendor's batch quote endpoint (`hq.sinajs.cn/list=...`) **does** carry
the finished session, and it is batched — one request per 60 symbols instead of
one per instrument. Measured on sh510300 at 19:3x:

| field | quote face | history face (next morning) |
|---|---|---|
| open / high / low / close | 4.155 / 4.187 / 4.130 / 4.179 | same |
| volume (shares) | 2,119,844,708 | same |
| amount (yuan) | 8,817,683,336 | same |

Design (`quote_tail`, pure):

* accepted **only** when the quote's own session date equals the expected
  complete-bar date — an intraday snapshot can never be written as a bar,
  because before 15:30 the expected date is still yesterday;
* the quote's **昨收** must reproduce the local last close within `1e-6` — that
  is the identity check that catches a wrong symbol mapping or an unadjusted
  split, on the same as-traded basis the history face uses;
* append-only, one row, tail only; `U.validate_rows` still runs.

`merge_tail` had to learn one thing to coexist: a local row dated **after** the
history face's own last print is not a source rewrite (it is tonight's quote bar
the history face has not published yet), so it is counted as `beyond_source` and
tolerated instead of refusing the symbol. Rows *inside* the source window are
still identity-checked and still refuse on drift.

## Live result (2026-10-26, bm-c)

* full sweep: 1,724 symbols, **1,697 topped up from the quote face**, 0 quote
  refusals, 0 fetch failures, 0 invalid rows;
* `data/daily` tail dates after the sweep: **1,717 files at 2026-10-26**, 6 at
  2026-10-23 (no quote session — suspended/delisted, disclosed), 1 at 2026-09-22,
  1 at 2026-09-04 (frozen legacy copies);
* `exchange_calendar_audit` flips from `source_lag missing ['2026-10-26']` to
  **`in_sync`, effective 2026-10-26, missing none**;
* the executable ticket reports **`feed: current`, lag 0 day(s)**, priced on the
  2026-10-26 bar: `as_of=2026-10-26 beta=0.20 k=0.47 nav=1.4604`, book 47%
  cash, five names at 9.4% each;
* **the forward ledger's first real mark**: `APPENDED 1 bars -> 2026-10-26
  nav=1.0010 dd=0.00% cash=30%` — the milestone r1264 scheduled for 2026-10-28,
  delivered two days early, on genuinely same-evening data.

## Negative finding (recorded so nobody repeats it)

Eastmoney `push2his` was the first candidate and it worked for one afternoon
burst (2026-10-26 19:2x: 510300 bar with amount 8,817,683,336) and then refused
**every** subsequent request from this host — `RemoteDisconnected` on 3-of-3
retries, for both `1.510300` and `0.159915`, minutes later. It is therefore not
a viable bulk face for a 1,700-symbol sweep: whatever good it does, it cannot be
depended on twice. The quote face is the vendor-blessed same-evening path.

## Honesty / limits

* The quote face is a **snapshot**, not a transaction record: it is trustworthy
  only after the close, and only for the session whose date it prints. There is
  no adjustment factor in it, which is right for ETFs (as-traded) and would be
  wrong for single stocks under corporate actions — this mechanism is wired to
  the ETF panel only.
* 6 of 1,725 files still print 2026-10-23. They carry no quote session, which
  reads as suspended or delisted; they are disclosed in the sweep payload rather
  than backfilled.
* The sweep still costs one history request per symbol; the quote pass is 29
  requests for 1,697 bars.
## Addendum (same round, second window): the parity leg that would have cried wolf every evening

The first window died before committing, so this window absorbed the work above and
ran it end to end. It went green everywhere except one leg, and that leg was a real
consequence of the new mechanism rather than a slip:

`update_daily --selftest` leg D ("source parity") took the panel's newest local date
and demanded the *history* face carry that same date with identical values. After the
quote tail wrote tonight's finished session, that date is by construction ahead of
the history face for one evening (the history face publishes it the next morning), so
the leg reported `FAIL (source history changed!)` on 2026-10-26 while the panel was
correct. Left alone it would have failed every evening after a top-up -- or, worse,
trained the reader to ignore the one message that is supposed to mean "the vendor
rewrote history".

Fix: the comparison is now a pure function, `parity_verdict(hist, mine)`, that asserts
the values on the newest date **both** sides carry and returns the unverifiable tail
separately (`ahead`), so the disclosed readout is
`source parity 510300 @ 2026-10-23... PASS [local ahead of source by 1 bar(s) 2026-10-26..2026-10-26 -- quote-tail rows written before the history face publishes them, no source evidence yet]`.
A shared-bar disagreement is still loud and now names the column; duplicate dates in
the source are refused (`ambiguous`) rather than guessed; no overlap at all is `SKIP`.
Four offline legs pin the four branches (match-with-tail, mismatch-on-close,
no-overlap, missing frame), so the distinction cannot silently collapse again. Tomorrow
is the natural check: when the history face prints 2026-10-26, the same leg either
confirms the quote bar byte-identically or flags an `overlap_mismatch` on 510300 --
both outcomes are informative and neither rewrites history.

Second-window verification of the first window's claims (measured here, not repeated
from its notes): `etf_wide --selftest` 36/36; `data_lag_audit` **in_sync**, effective
2026-10-26, missing none; ticket `feed: current`, lag 0 day(s), 5 names + 53% cash on
the 2026-10-26 bar; forward ledger appended its first real mark (nav 1.0010); panel
tail counted independently file by file -- **1,717 at 2026-10-26, 6 at 2026-10-23,
2 frozen** (`510880_t73.csv` at 2026-09-22, a legacy suffixed copy the sweep already
skips by name, and `sh512390.csv` at 2026-09-04 -- a genuinely stopped ETF printing
tiny volume in its last month and absent from `eligibility.csv`, so it cannot enter
the book). smoke 72/72, `update_daily --selftest` green including the new legs.

## Two more defects the wiring exposed (both measured, both fixed here)

**3. A wired leg with a min() gate pays the full sweep every single round.** The first
chain run after wiring cost **361.4s and 1,724 history requests** -- and would have done
so on every 10-minute round, forever. Cause: `panel_cutoff()` is `min()` over the
universe (correct as a *disclosure*: "the oldest bar we carry"), and one suspended
symbol with no quote session pins that min at yesterday. On 2026-10-26 the min read
2026-09-04 (sh512390, stopped printing in September) so the "is the panel fresh?" gate
could never close, no matter how fresh 1,717 of 1,724 files were. E136 had already
settled this shape for the lag audit -- *staleness is a coverage question, not a min* --
so the gate now uses the same rule: `panel_coverage()` + `coverage_closes_gate()`, floor
**95%**, and it may only close a gate the calendar says could be open. Live:
`noop_fresh, coverage 99.88% of 1723 symbols already at 2026-10-26 (floor 95%);
laggards=2 sz159332,sz159355`, returned in ~2 seconds instead of six minutes. The two
laggards are the symbols whose quote face disagreed with the local last close
(`prev_close_drift`) and were therefore refused -- disclosed by name, not smoothed.
The original protection is intact: a handful of fresh files hiding 1,670 stale ones
scores a few percent, far under the floor. selftest 36 -> 40 legs.

**4. A lane status file in results/ was being read as a backtest face -- and killed the
whole dashboard.** `monitor/build_status.py` iterated `results/*.json`, took any dict with
`status == "ok"` as a backtest face, and did `d["metrics"]` -> `KeyError: 'metrics'` on
`results/etf_daily_pull_status.json`, so the CEO-visible status panel stopped rebuilding
(the chain leg reported rc=1 with a takeover message that hid the real traceback until
run by hand). Two fixes, both needed: the dashboard now requires an actual `metrics`
dict with numeric `sharpe/annual_return/max_drawdown`, skips status-only faces and
counts them (`n_status_only_skipped`); and the five-member lane stopped inheriting a
foreign body -- E138 moved the wide leg's *writes* to their own path but the five-member
face still loaded whatever was already in its file and merged on top, so the pre-split
wide payload (universe 1724, quote_topup_stems 1697) was still sitting inside it. It now
writes `owned_status(st)` = its own keys only (selftest 11 -> 12 legs). Live face after
the prune: `[data_cutoff, expected_cutoff, lane_owner, last_attempt, machine, mode,
no_op_reason, status, ts]`; dashboard rebuilt green: `factors=10
backtest=432combos/0pass traders=6 milestones=6/7`.
