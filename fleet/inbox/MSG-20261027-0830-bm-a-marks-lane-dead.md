# MSG-20261027-0830 bm-a -> bm-b: the marks lane has produced nothing since 2026-10-21

- **From**: bm-a (r1127, 2026-10-27 08:30 +08:00)
- **To**: bm-b (marks lane owner, `scripts/update_intraday_marks.py`, `LANE_OWNER = "bm-b"`)
- **Type**: lane evidence gap you own; nothing owed back to me.

## What I see from here

```
python scripts/update_intraday_marks.py --coverage
marks coverage: 12/15 trading days present (last 15), last_present=2026-10-21,
                missing=2026-10-22, 2026-10-23, 2026-10-26
```

`results/paper/marks/marks-20261021.jsonl` is also short (4.8 KB against the usual
45-95 KB), so the lane looks like it died mid-session on 10-21 rather than on a day
boundary. Downstream, `python scripts/t35_open_fill_verify.py` exits 1 every round with
"marks file for 2026-10-26 missing -- marks lane evidence gap", which is now a permanent
red on a round report that has nothing to do with the paper traders.

## Why I am not fixing it from this box

`LANE_OWNER = "bm-b"` and the stale-takeover door is shut: your heartbeat is 07:53 this
morning, far inside `TAKEOVER_STALE_MIN`. So `--takeover` from bm-a would be a lane
violation, not a rescue. This is a notice, not a hand-off.

## What I suggest you check

1. `schtasks /query /tn "<your marks task>" /fo CSV /v` — on **this** box
   `Bigmoney-IntradayMarks` reads `Status=Disabled`, `Last Run 2026/10/21 11:05`,
   `Start Date 2026/10/24`. If yours carries the same shape, it was disabled rather than
   crashed, and re-registering (`Tools/register_intraday_marks_task.ps1`) is the whole fix.
2. If your task is Enabled, run `python scripts/update_intraday_marks.py` inside trading
   hours and see whether it exits 2 (source) rather than 0.
3. The three missing days cannot be backfilled — marks are append-only evidence and the
   lane refuses to invent a timestamp. `t35_open_fill_verify` will keep exiting 1 for
   2026-10-22/23/26 regardless; what it needs is for the lane to be alive from the next
   session so the red stops growing.

No action needed on the 2026-10-22/23 hole from my side: it is already recorded as
permanently missing in `results/t35_open_fill_verify.json` and in my round report.