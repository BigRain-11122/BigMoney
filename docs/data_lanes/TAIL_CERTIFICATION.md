# Panel tail certification

As of 2026-11-12T03:49:10. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-11 | 2026-11-11 | yes | 10/10 | 9 (90.00%) |
| repo | 2026-11-10 | 2026-11-10 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-10 | 2026-11-10 | yes | 5225/5226 | 5225 (100.00%) |
| astock_daily | 2026-11-11 | 2026-11-11 | yes | 5223/5223 | 1985 (38.00%) |
| ah_panel | 2026-11-10 | 2026-11-10 | yes | 187/187 | 187 (100.00%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-12T01:10:17` (10/10 files unchanged)
- **repo**: carried from `2026-11-10T20:50:13` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-10T20:50:14` (5225/5226 files unchanged)
- **ah_panel**: carried from `2026-11-10T20:53:28` (187/187 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **futures** (1 of 10): TS.csv
- **astock_daily** (3238 of 5223): 000831.csv, 002129.csv, 002650.csv, 002717.csv, 003029.csv, 300264.csv, 300540.csv, 300541.csv, 300542.csv, 300543.csv, 300545.csv, 300546.csv, 300547.csv, 300548.csv, 300549.csv, 300550.csv, 300551.csv, 300552.csv, 300553.csv, 300554.csv, 300555.csv, 300556.csv, 300557.csv, 300558.csv, 300559.csv …
