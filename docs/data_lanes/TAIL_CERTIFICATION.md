# Panel tail certification

As of 2026-11-14T20:24:12. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-13 | 2026-11-13 | yes | 10/10 | 9 (90.00%) |
| repo | 2026-11-13 | 2026-11-13 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-10 | 2026-11-10 | yes | 5225/5226 | 5225 (100.00%) |
| astock_daily | 2026-11-13 | 2026-11-13 | yes | 5223/5223 | 5212 (99.79%) |
| ah_panel | 2026-11-13 | 2026-11-13 | yes | 187/187 | 106 (56.68%) |

## 3 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-13T21:01:43` (10/10 files unchanged)
- **repo**: carried from `2026-11-14T10:04:40` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-13T21:01:44` (5225/5226 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **futures** (1 of 10): TS.csv
- **astock_daily** (11 of 5223): 000056.csv, 000635.csv, 000831.csv, 002129.csv, 002717.csv, 002731.csv, 301139.csv, 600185.csv, 688121.csv, 688496.csv, 688798.csv
- **ah_panel** (81 of 187): 00347.csv, 00358.csv, 00390.csv, 00470.csv, 00588.csv, 00638.csv, 00670.csv, 00699.csv, 00753.csv, 00763.csv, 00916.csv, 00921.csv, 01055.csv, 01072.csv, 01081.csv, 01138.csv, 01157.csv, 01211.csv, 01304.csv, 01336.csv, 01375.csv, 01377.csv, 01618.csv, 01635.csv, 01772.csv …
