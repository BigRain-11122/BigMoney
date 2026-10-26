# DIGEST 2026-10-26 · E136 — the panel cannot tell a holiday from a dead feed

**Round:** r1286 (bm-c) · **Product:** `scripts/exchange_calendar_audit.py`,
`data/exchange_calendar.csv`, `results/data_lag_audit.json`

## What happened

The round's pointer was "the first real forward mark off the 2026-10-26 close".
At 16:45 on 2026-10-26 — an official trading day, more than an hour past the
close — every data leg reported nothing to do:

| leg | output |
|---|---|
| `update_daily` | `total_new_rows: 0`, `data_cutoff: 2026-10-23`, per-symbol `skipped: probe_no_new` |
| `update_etf_daily` | `no-op: panel cutoff 2026-10-23 covers expected complete-bar date 2026-10-23` |
| `etf_book_forward` | `NO-OP last_bar=2026-10-23 nav=1.0 (no new panel bars)` |
| S6 chain | 42/42 rc0 |

Nothing was broken in the sense the smoke suite can see. The book's forward
ledger simply did not accrue, and no leg is able to say whether that is correct.

## Why it is invisible

Every leg decides "is there anything expected today?" from a date it derives out
of **our own data**:

* `update_daily` probes one symbol (510300) and treats "no new row" as "no new
  calendar day";
* `update_etf_daily` / `update_astock_daily` compare against a local ETF
  calendar that is itself a union of our bar files
  (`scripts/build_trading_calendar.py`), so a missing bar cannot appear as a
  contradiction — it is simply absent from both sides;
* `data/trading_calendar.csv` on disk ends at **2026-09-30** and has no refresh
  leg at all.

A self-referential calendar always grades its own panel as complete.

## The fix

One independent factual reference and one face built on it.

`data/exchange_calendar.csv` — official SSE/SZSE trading days from sina
(`akshare.tool_trade_date_hist_sina`), 8,797 days 1990-12-19 → 2026-12-31, one
request. Refresh gate: only when coverage ends inside 30 days or the last
attempt is older than 6 h, so the steady state is zero network for the rest of
the year. Writes are unions with whatever is on disk — a calendar is history and
can never shrink. Malformed / duplicate rows are a mechanism failure, not a note.

`results/data_lag_audit.json` — reconciles that calendar against the local panel
and names the verdict:

| verdict | meaning |
|---|---|
| `in_sync` | the maintained panel covers every official day it should by now |
| `source_lag` | only today is missing, and the market has closed — publication delay, self-heals |
| `panel_gap` | an **older** official day is missing — the feed stopped, a human is needed |

Live reading at 16:55: **`source_lag`** — expected `2026-10-26`, active cohort
1,723/1,725, effective cutoff `2026-10-23`, missing `['2026-10-26']`. The forward
ledger is paused by the feed, not by us; the audit says so in one line, and
`forward_impact` names the ledger bar it is costing.

## Three boundary rules that are easy to get wrong (all pinned by selftest)

1. **15:30 accept time.** Before the close today's bar must not be required, or
   the audit fires a false alarm every morning (L4). This is the same boundary
   `update_daily` uses.
2. **Do not measure lag with `min()` over the panel.** `data/daily` holds 1,725
   CSVs; two of them stop at 2026-09-04/09-22. The first live run therefore
   reported a 10-day `panel_gap` while the maintained panel was one publication
   behind. Correct reading: the *maintained cohort* (tails within the last 5 official
   days of the newest tail) and ≥90 % coverage define "this day is covered"; the
   frozen cohort is disclosed separately (L9).
3. **A single laggard inside the cohort is data, not an outage** — it goes into
   `lagging_active_sample` and does not flip the verdict (L8).

## Wiring

* `Tools/s6_chain_bmc.py` — new leg `cal_audit` right behind `update_daily`
  (43 legs), so the verdict is measured at the same instant as the panel; the
  runner also gained `--only=<leg[,leg]>`, which removes the "re-run the whole
  chain because one leg is being debugged / because the tool killed the driver
  mid-flight" cost that r1185 recorded.
* `smoke_test.py` — two legs: the selftest exit-code contract, and a live-face
  check that `results/data_lag_audit.json` exists and speaks a known verdict
  (a green selftest on synthetic panels proves nothing about the published file;
  cf. the r1270 lesson).

## Verification

```
python scripts/exchange_calendar_audit.py selftest   # 9/9 PASS
python scripts/exchange_calendar_audit.py run        # rc=0, verdict=source_lag
python Tools/s6_chain_bmc.py --only=cal_audit 0      # rc=0 through the runner
python -m smoke_test                                 # 70/70 PASS, legs=43
```

## Carry-forward

The forward mark itself is still owed: it opens the moment `data_lag_audit`
turns `in_sync` (or `source_lag` clears), i.e. the first round whose
`etf_book_forward` sees a 2026-10-26 bar. The audit now makes that waiting
condition explicit and one round of it cannot pass unnoticed.