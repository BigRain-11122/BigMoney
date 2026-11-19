# Panel tail certification

As of 2026-11-20T03:24:30. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10656 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-19 | 2026-11-19 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-19 | 2026-11-19 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-17 | 2026-11-17 | yes | 5226/5227 | 5225 (99.98%) |
| astock_daily | 2026-11-19 | 2026-11-19 | yes | 5221/5221 | 3355 (64.26%) |
| ah_panel | 2026-11-19 | 2026-11-19 | yes | 187/187 | 185 (98.93%) |

## 3 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-20T00:49:47` (10/10 files unchanged)
- **moneyflow**: carried from `2026-11-19T11:09:12` (5226/5227 files unchanged)
- **ah_panel**: carried from `2026-11-20T00:50:35` (187/187 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **moneyflow** (1 of 5227): 002731.csv
- **astock_daily** (1866 of 5221): 000635.csv, 002717.csv, 002777.csv, 002778.csv, 002779.csv, 002780.csv, 002782.csv, 002783.csv, 002785.csv, 002786.csv, 002787.csv, 002788.csv, 002789.csv, 002790.csv, 002791.csv, 002792.csv, 002793.csv, 002795.csv, 002796.csv, 002797.csv, 002798.csv, 002799.csv, 002800.csv, 002801.csv, 002802.csv …
- **ah_panel** (2 of 187): 01812.csv, 02493.csv
