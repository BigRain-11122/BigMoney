# Panel tail certification

As of 2026-11-10T05:59:58. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-09 | 2026-11-09 | yes | 10/10 | 9 (90.00%) |
| repo | 2026-11-09 | 2026-11-09 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-09 | 2026-11-09 | yes | 5225/5226 | 5225 (100.00%) |
| astock_daily | 2026-11-09 | 2026-11-09 | yes | 5223/5223 | 3258 (62.38%) |
| ah_panel | 2026-11-09 | 2026-11-09 | yes | 187/187 | 187 (100.00%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-10T05:23:57` (10/10 files unchanged)
- **repo**: carried from `2026-11-10T05:23:57` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-10T05:23:57` (5225/5226 files unchanged)
- **ah_panel**: carried from `2026-11-10T05:26:29` (187/187 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **futures** (1 of 10): TS.csv
- **astock_daily** (1965 of 5223): 000007.csv, 000831.csv, 002129.csv, 002623.csv, 002717.csv, 301139.csv, 600082.csv, 600500.csv, 600501.csv, 600502.csv, 600503.csv, 600505.csv, 600506.csv, 600507.csv, 600508.csv, 600509.csv, 600510.csv, 600511.csv, 600512.csv, 600513.csv, 600515.csv, 600516.csv, 600517.csv, 600518.csv, 600519.csv …
