# Panel tail certification

As of 2026-11-10T20:50:13. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-09 | 2026-11-09 | yes | 10/10 | 9 (90.00%) |
| repo | 2026-11-10 | 2026-11-10 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-10 | 2026-11-10 | yes | 5225/5226 | 5225 (100.00%) |
| astock_daily | 2026-11-10 | 2026-11-10 | yes | 5223/5223 | 1213 (23.22%) |
| ah_panel | 2026-11-10 | 2026-11-10 | yes | 187/187 | 187 (100.00%) |

## 1 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-10T05:23:57` (10/10 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **futures** (1 of 10): TS.csv
- **astock_daily** (4010 of 5223): 000812.csv, 000831.csv, 002129.csv, 002717.csv, 002736.csv, 002737.csv, 002738.csv, 002739.csv, 002741.csv, 002742.csv, 002743.csv, 002745.csv, 002746.csv, 002747.csv, 002748.csv, 002749.csv, 002752.csv, 002753.csv, 002755.csv, 002756.csv, 002757.csv, 002758.csv, 002759.csv, 002760.csv, 002761.csv …
