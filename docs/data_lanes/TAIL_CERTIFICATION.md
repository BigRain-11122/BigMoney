# Panel tail certification

As of 2026-11-20T16:01:31. The board reads the big per-symbol panels through a 40-file sample; this reads every file and says whether the sample got the same answer — and how many symbols actually hold the newest bar.

Read on **bm-c**'s disk — another machine's board reads this as a foreign scan and will not quote these counts against its own copy.

Verdict: **certified** — 5 panel(s), 10657 file(s) scanned.

| lane | full tail | sample tail | agree | files read | symbols holding the newest bar |
|---|---|---|---|---|---|
| futures | 2026-11-19 | 2026-11-19 | yes | 10/10 | 10 (100.00%) |
| repo | 2026-11-19 | 2026-11-19 | yes | 11/11 | 11 (100.00%) |
| moneyflow | 2026-11-19 | 2026-11-19 | yes | 5227/5228 | 5226 (99.98%) |
| astock_daily | 2026-11-19 | 2026-11-19 | yes | 5221/5221 | 5214 (99.87%) |
| ah_panel | 2026-11-19 | 2026-11-19 | yes | 187/187 | 185 (98.93%) |

## 3 row(s) carried forward

A lane whose panel bytes are unchanged since it was last scanned is not re-read; its numbers stand as of that scan (the `as_of` above is the newest full read, not this run).

- **futures**: carried from `2026-11-20T00:49:47` (10/10 files unchanged)
- **repo**: carried from `2026-11-20T03:24:30` (11/11 files unchanged)
- **ah_panel**: carried from `2026-11-20T00:50:35` (187/187 files unchanged)


## Symbols whose last bar is behind the panel's newest bar

- **moneyflow** (1 of 5228): 002731.csv
- **astock_daily** (7 of 5221): 000635.csv, 002717.csv, 600185.csv, 600567.csv, 688121.csv, 688496.csv, 688798.csv
- **ah_panel** (2 of 187): 01812.csv, 02493.csv
