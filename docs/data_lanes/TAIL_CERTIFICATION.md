# Panel tail certification

As of 2026-11-13T05:11:24. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-12 | 2026-11-12 | yes | 10/10 | 9 (90.00%) |
| repo | 2026-11-11 | 2026-11-11 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-10 | 2026-11-10 | yes | 5225/5226 | 5225 (100.00%) |
| astock_daily | 2026-11-12 | 2026-11-12 | yes | 5223/5223 | 5210 (99.75%) |
| ah_panel | 2026-11-12 | 2026-11-12 | yes | 187/187 | 187 (100.00%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-12T23:44:45` (10/10 files unchanged)
- **repo**: carried from `2026-11-12T23:44:45` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-12T23:44:46` (5225/5226 files unchanged)
- **ah_panel**: carried from `2026-11-12T23:47:37` (187/187 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **futures** (1 of 10): TS.csv
- **astock_daily** (13 of 5223): 000631.csv, 000831.csv, 002129.csv, 002443.csv, 002717.csv, 301139.csv, 600185.csv, 603369.csv, 603538.csv, 688121.csv, 688496.csv, 688605.csv, 688798.csv
