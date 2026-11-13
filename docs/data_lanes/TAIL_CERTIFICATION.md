# Panel tail certification

As of 2026-11-14T02:10:05. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-13 | 2026-11-13 | yes | 10/10 | 9 (90.00%) |
| repo | 2026-11-13 | 2026-11-13 | yes | 11/11 | 9 (81.82%) |
| moneyflow | 2026-11-10 | 2026-11-10 | yes | 5225/5226 | 5225 (100.00%) |
| astock_daily | 2026-11-13 | 2026-11-13 | yes | 5223/5223 | 5070 (97.07%) |
| ah_panel | 2026-11-12 | 2026-11-12 | yes | 187/187 | 187 (100.00%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-13T21:01:43` (10/10 files unchanged)
- **repo**: carried from `2026-11-13T21:01:43` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-13T21:01:44` (5225/5226 files unchanged)
- **ah_panel**: carried from `2026-11-13T21:04:31` (187/187 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **futures** (1 of 10): TS.csv
- **repo** (2 of 11): GC001.csv, R-001.csv
- **astock_daily** (153 of 5223): 000001.csv, 000002.csv, 000006.csv, 000007.csv, 000008.csv, 000009.csv, 000010.csv, 000011.csv, 000012.csv, 000014.csv, 000017.csv, 000019.csv, 000020.csv, 000021.csv, 000025.csv, 000026.csv, 000027.csv, 000028.csv, 000029.csv, 000030.csv, 000031.csv, 000032.csv, 000034.csv, 000035.csv, 000036.csv …
