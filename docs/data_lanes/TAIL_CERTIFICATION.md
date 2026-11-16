# Panel tail certification

As of 2026-11-16T23:37:27. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10655 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-16 | 2026-11-16 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-13 | 2026-11-13 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-10 | 2026-11-10 | yes | 5225/5226 | 5225 (100.00%) |
| astock_daily | 2026-11-16 | 2026-11-16 | yes | 5221/5221 | 3631 (69.55%) |
| ah_panel | 2026-11-16 | 2026-11-16 | yes | 187/187 | 186 (99.47%) |

## 4 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-16T23:25:06` (10/10 files unchanged)
- **repo**: carried from `2026-11-16T23:25:06` (11/11 files unchanged)
- **moneyflow**: carried from `2026-11-16T23:25:06` (5225/5226 files unchanged)
- **ah_panel**: carried from `2026-11-16T23:27:51` (187/187 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **astock_daily** (1590 of 5221): 000635.csv, 000721.csv, 001301.csv, 001389.csv, 002235.csv, 002431.csv, 002717.csv, 600185.csv, 600429.csv, 600987.csv, 600988.csv, 600989.csv, 600990.csv, 600992.csv, 600993.csv, 600995.csv, 600996.csv, 600997.csv, 600998.csv, 600999.csv, 601000.csv, 601001.csv, 601002.csv, 601003.csv, 601005.csv …
- **ah_panel** (1 of 187): 01812.csv
